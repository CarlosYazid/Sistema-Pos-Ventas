from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import OrderProduct
from repositories.abc import BaseAssociationRepository


class OrderProductRepository(BaseAssociationRepository[OrderProduct]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(OrderProduct, fields_exclude)

    async def update(
        self, order_product: OrderProduct, session: AsyncSession
    ) -> OrderProduct | None:
        result = await session.exec(
            select(self.model).where(self._build_identity_filter(order_product))
        )

        obj = result.one_or_none()

        if not obj:
            return None

        obj.quantity = order_product.quantity
        session.add(obj)
        return obj
