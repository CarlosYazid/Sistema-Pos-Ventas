from sqlalchemy.sql.expression import Select
from sqlmodel.ext.asyncio.session import AsyncSession

from repositories import ProductRepository

from .abc import BaseService


class ProductService(BaseService[ProductRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(ProductRepository(fields_exclude))

    async def check_stock(self, _id: int, stock: int, session: AsyncSession) -> bool:
        return await self.repository.check_stock(_id, stock, session)

    async def check_expiration(self, _id: int, session: AsyncSession) -> bool:
        return await self.repository.check_expiration(_id, session)

    def search_low_stock_products(self) -> Select:
        return self.repository.search_low_stock_products()

    def search_expired_products(self) -> Select:
        return self.repository.search_expired_products()
