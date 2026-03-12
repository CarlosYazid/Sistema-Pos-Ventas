from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import OrderService
from repositories.abc import BaseAssociationRepository


class OrderServiceRepository(BaseAssociationRepository[OrderService]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(OrderService, fields_exclude)

    async def update(
        self, order_service: OrderService, session: AsyncSession
    ) -> OrderService | None:
        result = await session.exec(
            select(self.model).where(self._build_identity_filter(order_service))
        )

        obj = result.one_or_none()

        if not obj:
            return None

        obj.quantity = order_service.quantity
        session.add(obj)
        return obj
