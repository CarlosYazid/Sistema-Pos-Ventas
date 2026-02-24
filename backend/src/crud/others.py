from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Payment
from utils import PaymentUtils
from dtos import PaymentCreate, PaymentUpdate
from core import log_operation

class PaymentCrud:
    
    EXCLUDED_FIELDS_FOR_UPDATE = {"id"}
    
    @staticmethod
    @log_operation(True)
    async def create_payment(db_session: AsyncSession, payment: PaymentCreate) -> Payment:
        """Create a new payment."""
        
        try:
            
            # Create the payment
            new_payment = Payment(**payment.model_dump(exclude_unset=True))
            db_session.add(new_payment)
            
            await db_session.commit()
            await db_session.refresh(new_payment)
            
            return new_payment
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to create payment", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_payment(db_session: AsyncSession, payment_id: int) -> Payment:
        """Retrieve a payment by ID."""
        try:

            response = await db_session.exec(select(Payment).where(Payment.id == payment_id))
            payment = response.first()

            if payment is None:
                raise HTTPException(detail="Payment not found", status_code=404)

            return payment

        except Exception as e:
            raise HTTPException(detail="Failed to retrieve payment", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_payment(db_session: AsyncSession, fields: PaymentUpdate) -> Payment:
        """Update an existing payment."""

        # check if payment exists
        if not await PaymentUtils.exist_payment(db_session, fields.id):
            raise HTTPException(detail="Payment not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Payment).where(Payment.id == fields.id))
            payment = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():
                    
                if key in PaymentCrud.EXCLUDED_FIELDS_FOR_UPDATE:
                    continue
                    
                setattr(payment, key, value)

            db_session.add(payment)
            await db_session.commit()
            
            await db_session.refresh(payment)
            return payment
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to update payment", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_payment(db_session: AsyncSession, payment_id: int) -> bool:
        """Delete a payment by ID."""
        
        if not await PaymentUtils.exist_payment(db_session, payment_id):
            raise HTTPException(detail="Payment not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Payment).where(Payment.id == payment_id))

            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Failed to delete payment", status_code=500) from e
