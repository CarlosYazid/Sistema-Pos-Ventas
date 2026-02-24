from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from models import Service,  ServiceInput
from utils import ServiceUtils
from dtos import ServiceCreate, ServiceUpdate
from core import log_operation

class ServiceCrud:
    
    EXCLUDED_FIELDS_FOR_UPDATE = {"id"}

    @staticmethod
    @log_operation(True)
    async def create_service(db_session: AsyncSession, service: ServiceCreate) -> Service:
        """Create a new service."""
        
        try:
            
            new_service = Service(**service.model_dump(exclude_unset=True))
            db_session.add(new_service)
            
            await db_session.commit()    
            await db_session.refresh(new_service)
            
            return new_service
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Service creation failed", status_code=500) from e
        
    @staticmethod
    @log_operation(True)
    async def read_service(db_session: AsyncSession, service_id: int) -> Service:
        """Retrieve a service by ID."""
        
        try:
            
            result = await db_session.exec(select(Service).where(Service.id == service_id))
            service = result.first()

            if service is None:
                raise HTTPException(detail="Service not found", status_code=404)

            return service

        except Exception as e:
            raise HTTPException(detail="Service search failed", status_code=500) from e
        
    @staticmethod
    @log_operation(True)
    async def update_service(db_session: AsyncSession, fields: ServiceUpdate) -> Service:
        """Update an existing service."""
        
        if fields.id is None:
            raise HTTPException(detail="Service ID is required", status_code=400)
        
        # check if service exists
        if not await ServiceUtils.exist_service(db_session, fields.id):
            raise HTTPException(detail="Service not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Service).where(Service.id == fields.id))
            service = response.one()

            # update service
            for key, value in fields.model_dump(exclude_unset=True).items():

                if key in ServiceCrud.EXCLUDED_FIELDS_FOR_UPDATE:
                    continue

                setattr(service, key, value)

            db_session.add(service)
            await db_session.commit()    
                
            await db_session.refresh(service)
            return service
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Service update failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def delete_service(db_session: AsyncSession, service_id: int) -> bool:
        """Delete a service by ID."""

        # check if service exists
        if not await ServiceUtils.exist_service(db_session, service_id):
            raise HTTPException(detail="Service not found", status_code=404)

        from utils import OrderUtils

        # Check if the service is associated with any orders
        if await OrderUtils.exist_service_in_orders(db_session, service_id):
            raise HTTPException(detail="Cannot delete service with active orders", status_code=400)

        try:
            
            # delete service
            response = await db_session.exec(select(Service).where(Service.id == service_id))

            await db_session.delete(response.one())
            await db_session.commit()
            
            return True

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Service deletion failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def create_service_input(db_session: AsyncSession, service_input: ServiceInput) -> ServiceInput:
        """Create a new service input."""
        
        # check if service exists
        if not await ServiceUtils.exist_service(db_session, service_input.service_id):
            raise HTTPException(detail="Service not found", status_code=404)

        # check if product exists
        from utils import ProductUtils

        if not await ProductUtils.exist_product(db_session, service_input.product_id):
            raise HTTPException(detail="Product not found", status_code=404)
        
        # check if service input already exists
        if await ServiceUtils.exist_service_input(db_session, service_input):
            raise HTTPException(detail="Service input already exists", status_code=400)
        
        try:
            
            # create service input
            new_service_input = ServiceInput(**service_input.model_dump(exclude_unset=True))
            db_session.add(new_service_input)
            
            await db_session.commit()    
            await db_session.refresh(new_service_input)
            
            return new_service_input
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Service input creation failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_service_input(db_session: AsyncSession, service_input: ServiceInput) -> bool:
        """Delete a service input by service and product"""
        
        if not await ServiceUtils.exist_service_input(db_session, service_input):
            raise HTTPException(detail="Service input not found", status_code=404)
        
        try:
            
            # delete service input
            response = await db_session.exec(select(ServiceInput).where(ServiceInput.service_id == service_input.service_id).where(ServiceInput.product_id == service_input.product_id))

            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Service input deletion failed", status_code=500) from e
