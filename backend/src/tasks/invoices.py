import asyncio
from typing import Any
from datetime import datetime

from weasyprint import HTML
from celery import shared_task
from celery.utils.log import get_task_logger
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlmodel import Session, create_engine, select
from sqlalchemy.orm import selectinload

from core.settings import SETTINGS
from core.storage import get_e2_client
from models.order import Order, OrderProduct, OrderService, OrderStatus
from utils.order import OrderUtils

logger = get_task_logger(__name__)

SYNC_ENGINE = None
EMAIL_SERVICE = FastMail(SETTINGS.email_conf)
ORDER_UTILS = OrderUtils()

def get_sync_engine():
    
    global SYNC_ENGINE
    
    if SYNC_ENGINE is None:
        SYNC_ENGINE = create_engine(SETTINGS.db_url_sync, pool_pre_ping=True)
    
    return SYNC_ENGINE    

def build_payload(order: Order, tax_rate: float = 0.19) -> dict[str, Any]:

        items: list[dict[str, Any]] = []
        
        for order_product in order.order_products or []:
            
            if not order_product.product:
                continue
            
            unit_price = float(order_product.product.price)
            
            items.append({
                "type": "product",
                "name": order_product.product.name,
                "quantity": order_product.quantity,
                "unit_price": unit_price,
                "total": unit_price * order_product.quantity,
                })

        for order_service in order.order_services or []:
            
            if not order_service.service:
                continue
            
            unit_price = float(order_service.service.price)
            
            items.append({
                "type": "service",
                "name": order_service.service.name,
                "quantity": order_service.quantity,
                "unit_price": unit_price,
                "total": unit_price * order_service.quantity
                })
        
        subtotal = float(order.total_price or 0)
        tax_amount =  subtotal * tax_rate
        total = subtotal + tax_amount

        client = order.client
        client_name = ""
        
        if client:
            client_name = " ".join([client.first_name or "", client.last_name or ""]).strip()

        return {
            "invoice": {
                "number": order.id,
                "date": order.created_at.date(),
                "client": {
                    "name": client_name,
                    "email": client.email if client.email else "",
                    "phone": client.phone if client.phone else "",
                    },
                "subtotal": subtotal,
                "tax_rate": tax_rate,
                "tax_amount": tax_amount,
                "total": total
                },
            "items": items
        }

async def upload_invoice(pdf_bytes: bytes, key: str) -> None:
    
    await ORDER_UTILS.upload_invoice(
            pdf_bytes, 
            key, 
            get_e2_client())

def get_order(order_id: int) -> Order | None:
    
    with Session(get_sync_engine()) as session:
        result= session.exec(select(Order)
                .where(Order.id == order_id)
                .options(
                    selectinload(Order.order_products)
                    .selectinload(OrderProduct.product))
                .options(
                    selectinload(Order.order_services)
                    .selectinload(OrderService.service))
                .options(selectinload(Order.client)))
        return result.one_or_none()

@shared_task(bind=True, name="generate_invoice")
def generate_invoice(self, order_id: int, tax_rate: float = 0.19):
    
    order = get_order(order_id)
    
    if order is None:
        return  {
            "order": order_id,
            "verify_url": None,
            "status": "Not found",
        }

    if order.status == OrderStatus.PENDING:
        return {
            "order": order_id,
            "verify_url": None,
            "status": "Pending",
        }

    if order.status == OrderStatus.CANCELLED:
        return {
            "order": order_id,
            "verify_url": None,
            "status": "Cancelled",
        }
    
    if order.verification_token:
        return {
            "order": order.id,
            "verify_url": ORDER_UTILS.build_verify_url(order.verification_token),
            "status": "Already generated",
            }
    
    logger.info("Inicio de tarea de facturacion para orden: %s", order.id)

    try:
        
        data = build_payload(order)
        
        raw_token = ORDER_UTILS.create_token()
        verification_token = ORDER_UTILS.sign_token(raw_token)
        pdf_key = ORDER_UTILS.build_invoice_pdf_key(order_id, raw_token)
        verify_url = ORDER_UTILS.build_verify_url(verification_token)
        qr_data_url = ORDER_UTILS.generate_qr_data_url(verify_url)

        template = SETTINGS.jinja_env.get_template("invoice.html")
        
        html = template.render(
            invoice=data.get("invoice", {}),
            items=data.get("items", []),
            company={
                "name": SETTINGS.company_name,
                "email": SETTINGS.company_email,
                "phone": SETTINGS.company_phone,
                "address": SETTINGS.company_address,
                "footer_message": SETTINGS.footer_message,
            },
            qr_data_url=qr_data_url,
            verify_url=verify_url,
            current_year=datetime.now().year,
        )

        pdf_bytes = HTML(string=html, base_url=SETTINGS.templates_folder).write_pdf()
        
        asyncio.run(upload_invoice(pdf_bytes, pdf_key))
        
        logger.info("PDF subido a storage con key: %s", pdf_key)

        with Session(get_sync_engine()) as session:
            db_order = session.get(Order, order.id)
            db_order.verification_token = verification_token
            db_order.pdf_key = pdf_key
            session.commit()
        
        logger.info("Orden actualizada en la db. Orden: %s", order.id)
        
        client = data.get("invoice", {}).get("client", {})
        
        asyncio.run(
            EMAIL_SERVICE.send_message(MessageSchema(
                subject = f"Factura #{order.id}",
                recipients = [client.get("email", "")],
                template_body = {
                    'client_name': client.get("name", ""),
                    'verify_link': verify_url,
                    'company': {
                        'name': SETTINGS.company_name,
                        'logo': SETTINGS.company_logo,
                        'email': SETTINGS.company_email
                    },
                    'current_year' : datetime.now().date
                    },
                subtype = MessageType.html),
                template_name = "invoice_email.html")
            )
        
        logger.info("Email de factura enviado para orden: %s", order.id)

        logger.info("Fin de tarea de facturacion para orden: %s", order.id)
        
        return {
            "order": order.id,
            "verify_url": verify_url,
            "status": "ok",
        }

    except Exception as exc:
        
        logger.exception("Error en tarea de facturacion para orden: %s", order.id)
        
        raise self.retry(exc=exc)
