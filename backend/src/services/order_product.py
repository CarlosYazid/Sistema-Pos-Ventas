from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core import NotFoundError, UpdateError
from models import OrderProduct
from repositories import OrderProductRepository
from services.abc import BaseAssociationService


class OrderProductService(BaseAssociationService[OrderProductRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(OrderProductRepository(fields_exclude))

    async def update(self, order_product: OrderProduct, session: AsyncSession) -> OrderProduct:

        if not await self.repository.exists(order_product, session):
            raise NotFoundError(self.entity)

        try:
            order_product = await self.repository.update(order_product, session)

            await session.commit()
            await session.refresh(order_product)

            return order_product

        except SQLAlchemyError as e:
            await session.rollback()

            raise UpdateError(self.entity) from e
