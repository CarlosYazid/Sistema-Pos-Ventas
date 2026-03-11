from sqlmodel.ext.asyncio.session import AsyncSession

from core import NotFoundError
from models import ProductCategory
from repositories import CategoryRepository

from .abc import AbstractAssociationService, AbstractService, BaseService


class CategoryService(BaseService[CategoryRepository]):
    def __init__(
        self,
        fields_exclude: set[str] | None = None,
        product_service: AbstractService | None = None,
        product_category_service: AbstractAssociationService | None = None,
    ):
        super().__init__(CategoryRepository(fields_exclude))
        self.product_service = product_service
        self.product_category_service = product_category_service

    async def add_product(
        self, product_category: ProductCategory, session: AsyncSession
    ) -> ProductCategory:
        if not await self.exist(product_category.category_id, session):
            raise NotFoundError(self.entity)

        if not await self.product_service.exist(product_category.product_id, session):
            raise NotFoundError(self.product_service.entity)

        return await self.product_category_service.create(product_category, session)

    async def remove_product(
        self, product_category: ProductCategory, session: AsyncSession
    ) -> bool:
        return await self.product_category_service.delete(product_category, session)
