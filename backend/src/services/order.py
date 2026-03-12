from sqlmodel.ext.asyncio.session import AsyncSession

from core import (
    ExpiredProductError,
    InsufficientStockError,
    NotFoundError,
)
from models import OrderProduct
from models import OrderService as OrderServiceModel
from repositories import OrderRepository
from services.abc import AbstractAssociationService, AbstractService

from .abc import BaseService


class OrderService(BaseService[OrderRepository]):
    def __init__(
        self,
        fields_exclude: set[str] | None = None,
        product_service: AbstractService | None = None,
        service_service: AbstractService | None = None,
        order_product_service: AbstractAssociationService | None = None,
        order_service_service: AbstractAssociationService | None = None,
    ):
        super().__init__(OrderRepository(fields_exclude))
        self.product_service = product_service
        self.service_service = service_service
        self.order_product_service = order_product_service
        self.order_service_service = order_service_service

    async def add_product(self, order_product: OrderProduct, session: AsyncSession) -> OrderProduct:
        if not await self.exists(order_product.order_id, session):
            raise NotFoundError(self.entity)

        if not await self.product_service.exists(order_product.product_id, session):
            raise NotFoundError(self.product_service.entity)

        if not await self.product_service.check_stock(
            order_product.product_id, order_product.quantity, session
        ):
            raise InsufficientStockError(str(order_product.product_id))

        if not await self.product_service.check_expiration(order_product.product_id, session):
            raise ExpiredProductError(str(order_product.product_id))

        return await self.order_product_service.add(order_product, session)

    async def update_quantity_product(
        self, order_product: OrderProduct, session: AsyncSession
    ) -> OrderProduct:
        if not await self.product_service.check_stock(
            order_product.product_id, order_product.quantity, session
        ):
            raise InsufficientStockError(str(order_product.product_id))

        if not await self.product_service.check_expiration(order_product.product_id, session):
            raise ExpiredProductError(str(order_product.product_id))

        return await self.order_product_service.update(order_product, session)

    async def remove_product(self, order_product: OrderProduct, session: AsyncSession) -> bool:
        return await self.order_product_service.remove(order_product, session)

    async def add_service(
        self, order_service: OrderServiceModel, session: AsyncSession
    ) -> OrderServiceModel:
        if not await self.repository.exists(order_service.order_id, session):
            raise NotFoundError(self.entity)

        if not await self.service_service.exists(order_service.service_id, session):
            raise NotFoundError(self.service_service.entity)

        return await self.order_service_service.add(order_service, session)

    async def update_quantity_service(
        self, order_service: OrderServiceModel, session: AsyncSession
    ) -> OrderServiceModel:
        return await self.order_service_service.update(order_service, session)

    async def remove_service(self, order_service: OrderServiceModel, session: AsyncSession) -> bool:
        return await self.order_service_service.remove(order_service, session)
