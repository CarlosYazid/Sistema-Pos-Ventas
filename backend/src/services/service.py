from sqlmodel.ext.asyncio.session import AsyncSession

from core import (
    NotFoundError,
)
from models import ServiceInput
from repositories import ServiceRepository

from .abc import AbstractAssociationService, AbstractService, BaseService


class ServiceService(BaseService[ServiceRepository]):
    def __init__(
        self,
        fields_exclude: set[str] | None = None,
        product_service: AbstractService | None = None,
        service_input_service: AbstractAssociationService | None = None,
    ):
        super().__init__(ServiceRepository(fields_exclude))
        self.product_service = product_service
        self.service_input_service = service_input_service

    async def add_product(self, service_input: ServiceInput, session: AsyncSession) -> ServiceInput:
        if not await self.exists(service_input.service_id, session):
            raise NotFoundError(self.entity)

        if not await self.product_service.exists(service_input.product_id, session):
            raise NotFoundError(self.product_service.entity)

        return await self.service_input_service.add(service_input, session)

    async def remove_product(
        self, service_input: ServiceInput, session: AsyncSession
    ) -> ServiceInput:
        return await self.service_input_service.remove(service_input, session)
