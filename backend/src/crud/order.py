from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, delete, update

from models import Order, OrderService, OrderProduct, OrderStatus, Product
from utils import OrderUtils, UserUtils
from dtos import OrderCreate, OrderUpdate
from core import log_operation

class OrderCrud:
    
    EXCLUDED_FIELDS_FOR_UPDATE = {"id"}
    
    @staticmethod
    @log_operation(True)
    async def create_order(db_session: AsyncSession, order: OrderCreate) -> Order:
        """Create a new order."""
        
        if not await UserUtils.exist_client(db_session, order.client_id):
            raise HTTPException(detail="Client not found", status_code=404)
        
        if not await UserUtils.exist_employee(db_session, order.employee_id):
            raise HTTPException(detail="Employee not found", status_code=404)
        
        try:
            
            new_order = Order(**order.model_dump(exclude_unset=True))
            db_session.add(new_order)
             
            await db_session.commit()
            await db_session.refresh(new_order)

            if order.status is OrderStatus.COMPLETED:
                
                from services import OrderService
                
                await OrderService.update_inventory(db_session, 0 if new_order.id is None else new_order.id)

            return new_order
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Order creation failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_order(db_session: AsyncSession, order_id: int) -> Order:
        """Retrieve an order by ID."""
        
        try:

            response = await db_session.exec(select(Order).where(Order.id == order_id))
            order = response.first()

            if order is None:
                raise HTTPException(detail="Order not found", status_code=404)

            return order

        except Exception as e:
            raise HTTPException(detail="Failed to retrieve order", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_order_status(db_session: AsyncSession, order_id: int) -> OrderStatus:
        """Retrieve the status of an order."""

        if not await OrderUtils.exist_order(db_session, order_id):
            raise HTTPException(detail="Order not found", status_code=404)
        
        try:

            response = await db_session.exec(select(Order).where(Order.id == order_id))
            status = response.one().status
            
            return status
            
        except Exception as e:
            raise HTTPException(detail="Failed to retrieve order status", status_code=500) from e

    @classmethod
    @log_operation(True)
    async def update_order(cls,db_session: AsyncSession, fields: OrderUpdate) -> Order:
        """Update an existing order."""

        if not await OrderUtils.exist_order(db_session, fields.id):
            raise HTTPException(detail="Order not found", status_code=404)

        try:
            
            response = await db_session.exec(select(Order).where(Order.id == fields.id))
            order = response.one()

            for key, value in fields.model_dump(exclude_unset=True).items():
                    
                if key in cls.EXCLUDED_FIELDS_FOR_UPDATE:
                    continue
                    
                setattr(order, key, value)

            db_session.add(order)
            await db_session.commit()
            
            await db_session.refresh(order)
            
            if order.status is OrderStatus.COMPLETED:

                from services import OrderService

                await OrderService.update_inventory(db_session, 0 if order.id is None else order.id)

            return order
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to update order", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def update_order_status(db_session: AsyncSession, order_id: int, status: OrderStatus) -> Order:
        """Update the status of an order."""

        if not await OrderUtils.exist_order(db_session, order_id):
            raise HTTPException(detail="Order not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Order).where(Order.id == order_id))
            order = response.one()
            
            order.status = status

            db_session.add(order)
            
            await db_session.commit()
            await db_session.refresh(order)

            if status is OrderStatus.COMPLETED:

                from services import OrderService

                await OrderService.update_inventory(db_session, 0 if order.id is None else order.id)

            return order
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to update order status", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_order(db_session: AsyncSession, order_id: int) -> None:
        """Delete an order by ID."""
        
        # Check if the order exists before attempting to delete
        if not await OrderUtils.exist_order(db_session, order_id):
            raise HTTPException(detail="Order not found", status_code=404)
        
        # Ensure the order is not completed before deleting
        if await OrderCrud.read_order_status(db_session, order_id) is OrderStatus.COMPLETED:
            raise HTTPException(detail="Cannot delete a completed order", status_code=400)
        
        try:
            
            response = await db_session.exec(select(Order).where(Order.id == order_id))
            
            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
            
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to delete order", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def create_order_service(db_session: AsyncSession, order_service: OrderService) -> OrderService:
        """Add a service to an order."""

        # Ensure the order_id exists before adding the service
        if not await OrderUtils.exist_order(db_session, order_service.order_id):
            raise HTTPException(detail="Order not found", status_code=404)

        if await OrderCrud.read_order_status(db_session, order_service.order_id) is OrderStatus.COMPLETED:
            raise HTTPException(detail="Cannot add service to a completed order", status_code=400)

        # Import ServiceCrud directly from its file path
        from utils import ServiceUtils

        # Ensure the service_id exists before adding the service
        if not await ServiceUtils.exist_service(db_session, order_service.service_id):
            raise HTTPException(detail="Service not found", status_code=404)
        
        try:
                
            db_session.add(order_service)
            
            await db_session.commit()
            await db_session.refresh(order_service)
            
            return order_service
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to add service to order", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_order_serivce(db_session: AsyncSession, order_service: OrderService) -> OrderService:
        """Update order service"""
        
        # Check if the order service exists before attempting to update
        if not await OrderUtils.exist_order_service(db_session, order_service):
            raise HTTPException(detail="Order service not found", status_code=404)
        
        if await OrderUtils.order_service_in_order_completed(db_session, order_service):
            raise HTTPException(detail="Order service in order completed", status_code=404)

        try:
            
            response = await db_session.exec(select(OrderService).where(OrderService.order_id == order_service.order_id).where(OrderService.service_id == order_service.service_id))
            _order_service = response.one()
            
            _order_service.quantity = order_service.quantity

            db_session.add(_order_service)
            
            await db_session.commit()
            await db_session.refresh(order_service)

            return order_service
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to update order service", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_order_services_by_service(db_session: AsyncSession, service_id: int) -> bool:
        """Delete all order services associated with a specific service."""

        from utils import ServiceUtils

        # Ensure the service_id exists before deleting order services
        if not await ServiceUtils.exist_service(db_session, service_id):
            raise HTTPException(detail="Service not found", status_code=404)

        try:

            await db_session.exec(delete(OrderService).where(OrderService.service_id == service_id))
                
            return True

        except Exception as e:
            raise HTTPException(detail="Failed to delete order services", status_code=500) from e    
    
    @staticmethod
    @log_operation(True)
    async def delete_order_service(db_session: AsyncSession, order_service: OrderService) -> bool:
        """Delete order services"""
        
        from utils import OrderUtils
        
        if not await OrderUtils.exist_order(db_session, order_service.order_id):
            raise HTTPException(detail="Order not found", status_code=404)
        
        # Check if the order service exists before attempting to delete
        if not await OrderUtils.exist_order_service(db_session, order_service):
            raise HTTPException(detail="Order service not found", status_code=404)

        if await OrderUtils.order_service_in_order_completed(db_session, order_service):
            raise HTTPException(detail="Order service in order completed", status_code=404)

        try:
            response = await db_session.exec(select(OrderService).where(OrderService.order_id == order_service.order_id).where(OrderService.service_id == order_service.service_id))
            
            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to delete order service", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def create_order_product(db_session: AsyncSession, order_product: OrderProduct) -> OrderProduct:
        """Add a product to an order."""

        # Ensure the order_id exists before adding the product
        if not await OrderUtils.exist_order(db_session, order_product.order_id):
            raise HTTPException(detail="Order not found", status_code=404)

        if await OrderCrud.read_order_status(db_session, order_product.order_id) is OrderStatus.COMPLETED:
            raise HTTPException(detail="Cannot add product to a completed order", status_code=400)

        # Import ProductUtils directly from its file path
        from utils import ProductUtils

        # Ensure the product_id exists before adding the product
        if not await ProductUtils.exist_product(db_session, order_product.product_id):
            raise HTTPException(detail="Product not found", status_code=404)
        
        from models import Product
        
        try:
            
            response = await db_session.exec(select(Order).where(Order.id == order_product.order_id))
            order = response.one()
                
            response = await db_session.exec(select(Product.price).where(Product.id == order_product.product_id))
            price_product = response.one()

            order.total_price = (order_product.quantity * price_product) + order.total_price

            db_session.add(order)
            db_session.add(order_product)
            await db_session.commit()
            
            await db_session.refresh(order_product)
            return order_product
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to add product to order", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_order_product(db_session: AsyncSession, order_product: OrderProduct) -> OrderProduct:
        """Update order product"""
        
        # Check if the order product exists before attempting to update
        if not await OrderUtils.exist_order_product(db_session, order_product):
            raise HTTPException(detail="Order product not found", status_code=404)
        
        if await OrderUtils.order_product_in_order_completed(db_session, order_product):
            raise HTTPException(detail="Order product in order completed", status_code=404)

        try:
            
            response = await db_session.exec(select(OrderProduct).where(OrderProduct.order_id == order_product.order_id).where(OrderProduct.product_id == order_product.product_id))
            _order_product = response.one()
            
            _order_product.quantity = order_product.quantity

            db_session.add(_order_product)
            
            await db_session.commit()
            await db_session.refresh(order_product)

            return order_product
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to update order product", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_order_products_by_product(db_session: AsyncSession, product_id: int) -> bool:
        """Delete all order products associated with a specific product."""

        from utils import ProductUtils

        # Ensure the product_id exists before deleting order products
        if not await ProductUtils.exist_product(db_session, product_id):
            raise HTTPException(detail="Product not found", status_code=404)

        try:

            await db_session.exec(delete(OrderProduct).where(OrderProduct.product_id == product_id))
                
            return True

        except Exception as e:
            raise HTTPException(detail="Failed to delete order products", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_order_product(db_session: AsyncSession, order_product: OrderProduct) -> bool:
        """Delete an order product"""
        
        # Check if the order product exists before attempting to delete
        if not await OrderUtils.exist_order_product(db_session, order_product):
            raise HTTPException(detail="Order product not found", status_code=404)

        if await OrderUtils.order_product_in_order_completed(db_session, order_product):
            raise HTTPException(detail="Order product in order completed", status_code=404)

        try:
            response = await db_session.exec(select(OrderProduct).where(OrderProduct.order_id == order_product.order_id).where(OrderProduct.product_id == order_product.product_id))
            order_product = response.one()
            
            await db_session.delete(order_product)
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to delete order product", status_code=500) from e
