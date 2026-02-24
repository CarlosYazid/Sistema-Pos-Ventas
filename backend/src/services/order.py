from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, update
from sqlalchemy.sql.expression import Select

from models import Order, OrderProduct, OrderService, OrderStatus, Product
from utils import OrderUtils
from dtos import OrderFilter, OrderProductFilter, OrderServiceFilter
from core import log_operation
class OrderService:
    
    QUERY_ORDER_BASE = select(Order)
    QUERY_ORDER_SERVICE_BASE = select(OrderService)
    QUERY_ORDER_PRODUCT_BASE = select(OrderProduct)
        
    @classmethod
    def search_orders(cls, filters: OrderFilter) -> Select:
        """Query that searches for orders who meet the filters."""
        return filters.apply(cls.QUERY_ORDER_BASE)

    @classmethod
    def search_order_services(cls, filters: OrderServiceFilter) -> Select:
        """Query that searches for orders service who meet the filters."""
        return filters.apply(cls.QUERY_ORDER_SERVICE_BASE)

    @classmethod
    def search_order_products(cls, filters: OrderProductFilter) -> Select:
        """Query that searches for orders product who meet the filters."""
        return filters.apply(cls.QUERY_ORDER_PRODUCT_BASE)
    
    @classmethod
    @log_operation(True)
    async def update_inventory(cls, db_session: AsyncSession, order_id: int) -> bool:
        """Update inventory after an order is placed"""

        if not await OrderUtils.exist_order(db_session, order_id):
            raise HTTPException(detail="Order not found", status_code=404)

        try:

            result = await db_session.exec(cls.search_orders_products(OrderProductFilter(order_id)))
            order_products = result.all()

            if not order_products:
                return True

            totals = {
                op.product_id: op.quantity for op in order_products
            }
        
            for product_id, qty in totals.items():
                stmt = (
                    update(Product)
                    .where(Product.id == product_id)
                    .values(stock=func.greatest(Product.stock - qty, 0))
                )
                await db_session.exec(stmt)

            await db_session.commit()
            
            return True
        
        except Exception as e:
            raise HTTPException(detail="Failed updating inventory", status_code=500)
