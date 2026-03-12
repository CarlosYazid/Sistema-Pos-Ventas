from sqlmodel.ext.asyncio.session import AsyncSession

from core import NotFoundError
from models import Product, ProductCategory
from repositories import CategoryRepository

from .abc import AbstractAssociationService, AbstractService, BaseService


class CategoryService(BaseService[CategoryRepository]):
    def __init__(
        self,
        fields_exclude: set[str] | None = None,
        product_service: AbstractService[Product] | None = None,
        product_category_service: AbstractAssociationService[ProductCategory] | None = None,
    ):
        super().__init__(CategoryRepository(fields_exclude))
        self.product_service = product_service
        self.product_category_service = product_category_service

    async def add_product(
        self, product_category: ProductCategory, session: AsyncSession
    ) -> ProductCategory:

        if not await self.exists(product_category.category_id, session):
            raise NotFoundError(self.entity)

        if not await self.product_service.exists(product_category.product_id, session):
            raise NotFoundError(self.product_service.entity)

        return await self.product_category_service.add(product_category, session)

    async def remove_product(
        self, product_category: ProductCategory, session: AsyncSession
    ) -> bool:
        return await self.product_category_service.remove(product_category, session)
