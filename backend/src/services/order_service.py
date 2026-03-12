from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core import NotFoundError, UpdateError
from models import OrderService
from repositories import OrderServiceRepository
from services.abc import BaseAssociationService


class OrderServiceService(BaseAssociationService[OrderServiceRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(OrderServiceRepository(fields_exclude))

    async def update(self, order_service: OrderService, session: AsyncSession) -> OrderService:
        if not await self.repository.exist(order_service, session):
            raise NotFoundError(self.entity)

        try:
            order_service = await self.repository.update(order_service, session)

            await session.commit()
            await session.refresh(order_service)

            return order_service

        except SQLAlchemyError as e:
            await session.rollback()

            raise UpdateError(self.entity) from e
