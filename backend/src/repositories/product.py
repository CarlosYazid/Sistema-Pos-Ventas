from datetime import date

from sqlalchemy.sql.expression import Select
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Product

from .abc import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Product, fields_exclude)

    async def check_stock(self, _id: int, stock: int, session: AsyncSession) -> bool:
        result = await session.exec(
            select(Product.id).where(Product.id == _id).where(Product.stock >= stock)
        )

        return bool(result.one_or_none())

    async def check_expiration(self, _id: int, session: AsyncSession) -> bool:
        result = await session.exec(
            select(Product.id)
            .where(Product.id == _id)
            .where(Product.expiration_date > date.today())
        )

        return bool(result.one_or_none())

    def search_low_stock_products(self) -> Select:
        """Query for search products with low stock."""
        return (
            self.base_query().where(Product.stock <= Product.minimum_stock).order_by(Product.stock)
        )

    def search_expired_products(self) -> Select:
        """Query for search products that are expired."""
        return (
            self.base_query()
            .where(Product.expiration_date < date.today())
            .order_by(Product.expiration_date)
        )
