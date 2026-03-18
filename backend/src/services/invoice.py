from typing import Any

from botocore.client import BaseClient
from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.errors import NotFoundError
from models import Order, OrderStatus
from schemas import InvoiceCreate
from services import AbstractService
from tasks import generate_invoice
from utils.order import OrderUtils

from .file import FileService


class InvoiceService:
    def __init__(
        self, order_service: AbstractService[Order], file_service: FileService, utils: OrderUtils
    ) -> None:
        self.order_service = order_service
        self.file_service = file_service
        self.utils = utils

    async def create_invoice(self, fields: InvoiceCreate, session: AsyncSession) -> dict[str, Any]:
        """Crea el token y encola la tarea para generar la factura."""

        if not await self.order_service.exists(fields.order_id, session):
            raise NotFoundError("Order")

        task = generate_invoice.delay(**fields.model_dump(exclude_none=True))

        return {"task": task.id, "status": "queued"}

    async def get_invoice(
        self, verification_token: str, session: AsyncSession, storage_client: BaseClient
    ) -> StreamingResponse:
        """Valida el token y retorna el PDF desde el storage."""

        if self.utils.verify_signature(verification_token) is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid verification token"
            )

        result = await session.exec(
            select(Order).where(Order.verification_token == verification_token)
        )

        order = result.one_or_none()

        if not order:
            raise NotFoundError("Invoice")

        if order.status == OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invoice access revoked"
            )

        return await self.file_service.get_file(order.pdf_key, storage_client)
