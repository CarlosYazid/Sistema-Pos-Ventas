from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core import InsufficientStockError, NotFoundError, UpdateError
from models import Order, OrderProduct, OrderStatus, Product
from schemas import OrderUpdate
from services.abc import AbstractService


class InventoryService:
    def __init__(self, order_service: AbstractService[Order]):
        self.order_service = order_service

    async def update_inventory(self, order_id: int, session: AsyncSession) -> Order | None:

        if not await self.order_service.exists(order_id, session):
            raise NotFoundError(self.order_service.entity)

        try:
            # Lock of products
            lock_stmt = (
                select(Product.name, Product.stock, Product.price, OrderProduct.quantity)
                .join(OrderProduct, OrderProduct.product_id == Product.id)
                .where(OrderProduct.order_id == order_id)
                .with_for_update()
            )

            result = await session.execute(lock_stmt)
            rows = result.all()

            if not rows:
                return None

            # Validation
            for row in rows:
                if row.stock < row.quantity:
                    raise InsufficientStockError(row.name)

            subq = (
                select(OrderProduct.product_id, OrderProduct.quantity)
                .where(OrderProduct.order_id == order_id)
                .subquery()
            )

            update_stmt = (
                update(Product)
                .where(Product.id == subq.c.product_id)
                .values(stock=Product.stock - subq.c.quantity)
            )

            await session.execute(update_stmt)

            total = sum(row.quantity * row.price for row in rows)

            order = await self.order_service.update(
                OrderUpdate(id=order_id, total_price=total, status=OrderStatus.COMPLETED), session
            )

            return order

        except SQLAlchemyError as e:
            await session.rollback()
            raise UpdateError(self.order_service.entity) from e
