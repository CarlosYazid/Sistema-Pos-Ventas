import asyncio
from datetime import datetime

from celery import shared_task
from fastapi_mail import FastMail, MessageSchema, MessageType
from sqlmodel import Session, create_engine

from core.settings import SETTINGS
from models.alert import ExpirationAlert, StockAlert

SYNC_ENGINE = None
EMAIL_SERVICE = FastMail(SETTINGS.email_conf)


def get_sync_engine():

    global SYNC_ENGINE

    if SYNC_ENGINE is None:
        SYNC_ENGINE = create_engine(SETTINGS.db_url_sync, pool_pre_ping=True)

    return SYNC_ENGINE


@shared_task(name="low_stock_alerts")
def low_stock_alerts():

    prods = None

    with Session(get_sync_engine()) as session:
        prods = session.query(StockAlert).where(StockAlert.notified == False).all()

    if not prods:
        return

    asyncio.run(
        EMAIL_SERVICE.send_message(
            message=MessageSchema(
                subject="Alerta: productos con stock bajo",
                recipients=[SETTINGS.company_email],
                template_body={
                    "company": {"name": SETTINGS.company_name, "logo": SETTINGS.company_logo},
                    "items": prods,
                    "current_year": datetime.now().year,
                    "inventory_url": SETTINGS.inventory_url,
                },
                subtype=MessageType.html,
            ),
            template_name="email_low_stock_products.html",
        )
    )

    for expired_alert in prods:
        expired_alert.notified = True

    with Session(get_sync_engine()) as session:
        session.add_all(prods)
        session.commit()


@shared_task(name="expired_alerts")
def expired_alerts():

    prods = None

    with Session(get_sync_engine()) as session:
        prods = session.query(ExpirationAlert).where(ExpirationAlert.notified == False).all()

    if not prods:
        return

    asyncio.run(
        EMAIL_SERVICE.send_message(
            message=MessageSchema(
                subject="Alerta: productos vencidos",
                recipients=[SETTINGS.company_email],
                template_body={
                    "company": {"name": SETTINGS.company_name, "logo": SETTINGS.company_logo},
                    "items": prods,
                    "current_year": datetime.now().year,
                    "inventory_url": SETTINGS.inventory_url,
                },
                subtype=MessageType.html,
            ),
            template_name="email_expired_products.html",
        )
    )

    for expired_alert in prods:
        expired_alert.notified = True

    with Session(get_sync_engine()) as session:
        session.add_all(prods)
        session.commit()
