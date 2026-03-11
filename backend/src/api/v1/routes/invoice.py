from fastapi import APIRouter, BackgroundTasks, Depends

from core import require_scope
from models import InvoiceRequest
from services import InvoiceService

router = APIRouter(prefix="/invoice", tags=["Invoice"])

INVOICE_SERVICE = InvoiceService()


@router.post("/generate")
async def generate_invoice(
    invoice_request: InvoiceRequest,
    background_tasks: BackgroundTasks,
    _: object = Depends(require_scope("invoices:write")),
):
    invoice = await INVOICE_SERVICE.workflow(
        order_id=invoice_request.order_id, tax_rate=invoice_request.tax_rate
    )
    background_tasks.add_task(INVOICE_SERVICE.send_invoice_email, invoice=invoice)
    await INVOICE_SERVICE.upload_invoice(invoice)
    return invoice
