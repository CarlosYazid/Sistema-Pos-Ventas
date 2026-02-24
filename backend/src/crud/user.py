from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Client, Employee
from utils import UserUtils
from dtos import ClientCreate, ClientUpdate, EmployeeCreate, EmployeeUpdate
from core import log_operation

class UserCrud:
    """CRUD operations for users"""
    
    EXCLUDED_FIELDS_FOR_UPDATE_USER = {"id", "documentid"}
    
    @staticmethod
    @log_operation(True)
    async def create_employee(db_session : AsyncSession, employee : EmployeeCreate) -> Employee:
        """Create a new employee."""
        
        try:
            
            new_employee = Employee(**employee.model_dump(exclude_unset=True))
            db_session.add(new_employee)

            await db_session.commit()
            await db_session.refresh(new_employee)
            
            return new_employee
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee creation failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def read_employee(db_session: AsyncSession, employee_id: int) -> Employee:
        """Retrieve an employee by ID."""
        
        try:

            response = await db_session.exec(select(Employee).where(Employee.id == employee_id))
            employee = response.first()
            
            if employee is None:
                raise HTTPException(detail="Employee not found", status_code=404)
            
            return employee

        except Exception as e:
            raise HTTPException(detail="Employee retrieval failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def read_employee_by_email(db_session: AsyncSession, email: str) -> Employee:
        """Retrieve an employee by email."""
        
        try:
        
            response = await db_session.exec(select(Employee).where(Employee.email == email))
            employee = response.first()
            
            if employee is None:
                raise HTTPException(detail="Employee not found", status_code=404)
            
            return employee

        except Exception as e:
            raise HTTPException(detail="Employee retrieval failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_employee_by_documentid(db_session: AsyncSession, document_id: int) -> Employee:
        """Retrieve an employee by document ID."""
        
        try:

            response = await db_session.exec(select(Employee).where(Employee.documentid == document_id))
            employee = response.first()
        
            if employee is None:
                raise HTTPException(detail="Employee not found", status_code=404)

            return employee

        except Exception as e:
            raise HTTPException(detail="Employee retrieval failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def update_employee(db_session: AsyncSession, fields: EmployeeUpdate) -> Employee:
        """Update an existing employee."""
        
        if fields.id is None:
            raise HTTPException(detail="Employee ID is required", status_code=400)
        
        if not await UserUtils.exist_employee(db_session, fields.id):
            raise HTTPException(detail="Employee not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Employee).where(Employee.id == fields.id))
            employee = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():
                
                    if key in UserCrud.EXCLUDED_FIELDS_FOR_UPDATE_USER:
                        continue
                
                    setattr(employee, key, value)

            db_session.add(employee)
            await db_session.commit()
            
            await db_session.refresh(employee)
            return employee

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee update failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def update_employee_by_email(db_session: AsyncSession, fields: EmployeeUpdate) -> Employee:
        """Update an existing employee by email."""
        
        if fields.email is None:
            raise HTTPException(detail="Employee email is required", status_code=400)

        if not await UserUtils.exist_employee_by_email(db_session, fields.email):
            raise HTTPException(detail="Employee not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Employee).where(Employee.email == fields.email))
            employee = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():
                
                if key in UserCrud.EXCLUDED_FIELDS_FOR_UPDATE_USER:
                    continue
                if key == "email":
                    continue

                setattr(employee, key, value)
            
            db_session.add(employee)
            await db_session.commit()

            await db_session.refresh(employee)
            return employee
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee update failed", status_code=500) from e

    
    @staticmethod
    @log_operation(True)
    async def update_employee_by_documentid(db_session: AsyncSession, fields: EmployeeUpdate) -> Employee:
        """Update an existing employee by document ID."""
        
        if fields.documentid is None:
            raise HTTPException(detail="Employee document ID is required", status_code=400)

        if not await UserUtils.exist_employee_by_documentid(db_session, fields.documentid):
            raise HTTPException(detail="Employee not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Employee).where(Employee.documentid == fields.documentid))
            employee = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():

                if key in UserCrud.EXCLUDED_FIELDS_FOR_UPDATE_USER:
                    continue
                    
                setattr(employee, key, value)

            db_session.add(employee)
            await db_session.commit()
                
            await db_session.refresh(employee)
            return employee

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_employee(db_session: AsyncSession, employee_id: int) -> bool:
        """Delete an employee by ID."""
        
        if not await UserUtils.exist_employee(db_session, employee_id):
            raise HTTPException(detail="Employee not found", status_code=404)

        # check if the employee have any orders
        from utils import OrderUtils
        
        if await OrderUtils.exist_orders_by_employee(db_session, employee_id):
            raise HTTPException(detail="Cannot delete employee with active orders. Consider disabling your status.", status_code=400)

        try:
            
            response = await db_session.exec(select(Employee).where(Employee.id == employee_id))
            
            await db_session.delete(response.one())
            await db_session.commit()
                
            return True

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee deletion failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_employee_by_email(db_session: AsyncSession, email: str) -> bool:
        """Delete an employee by email."""
        
        if not await UserUtils.exist_employee_by_email(db_session, email):
            raise HTTPException(detail="Employee not found", status_code=404)
        
        id_ = await UserUtils.translate_email_by_employee_id(db_session, email)
        
        # check if the employee have any orders
        from utils import OrderUtils
        
        if await OrderUtils.exist_orders_by_employee(db_session, id_):
            raise HTTPException(detail="Cannot delete employee with active orders. Consider disabling your status.", status_code=400)

        try:
            
            response = await db_session.exec(select(Employee).where(Employee.email == email))
            
            await db_session.delete(response.one())
            await db_session.commit()

            return True

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee deletion failed", status_code=500) from e

    @staticmethod
    @log_operation(True)
    async def delete_employee_by_documentid(db_session: AsyncSession, document_id: int) -> bool:
        """Delete an employee by document ID."""
        
        if not await UserUtils.exist_employee_by_documentid(db_session, document_id):
            raise HTTPException(detail="Employee not found", status_code=404)

        id_ = await UserUtils.translate_documentid_by_employee_id(db_session, document_id)

        # check if the employee have any orders
        from utils import OrderUtils
        
        if await OrderUtils.exist_orders_by_employee(db_session, id_):
            raise HTTPException(detail="Cannot delete employee with active orders. Consider disabling your status.", status_code=400)

        try:
            
            response = await db_session.exec(select(Employee).where(Employee.documentid == document_id))
            
            await db_session.delete(response.one())
            await db_session.commit()
                
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Employee deletion failed", status_code=500) from e
        
    @staticmethod
    @log_operation(True)
    async def create_client(db_session: AsyncSession, client_: ClientCreate) -> Client:
        """Create a new client."""
        
        try:
                
            client = Client(**client_.model_dump(exclude_unset=True))
            db_session.add(client)
            
            await db_session.commit()
            await db_session.refresh(client)
            
            return client
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client creation failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_client(db_session: AsyncSession, client_id: int) -> Client:
        """Retrieve a client by ID."""
        
        try:

            response = await db_session.exec(select(Client).where(Client.id == client_id))
            client = response.first()

            if client is None:
                raise HTTPException(detail="Client not found", status_code=404)

            return client

        except Exception as e:
            raise HTTPException(detail="Client retrieval failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_client_by_email(db_session: AsyncSession, email: str) -> Client:
        """Retrieve a client by email."""
        
        try:

            response = await db_session.exec(select(Client).where(Client.email == email))
            client = response.first()

            if client is None:
                raise HTTPException(detail="Client not found", status_code=404)

            return client

        except Exception as e:
            raise HTTPException(detail="Client retrieval failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def read_client_by_documentid(db_session: AsyncSession, document_id: int) -> Client:   
        """Retrieve a client by document ID."""
        try:

            response = await db_session.exec(select(Client).where(Client.documentid == document_id))
            client = response.first()

            if client is None:
                raise HTTPException(detail="Client not found", status_code=404)

            return client

        except Exception as e:
            raise HTTPException(detail="Client retrieval failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_client(db_session: AsyncSession, fields: ClientUpdate) -> Client:
        """Update an existing client."""
        
        if fields.id is None:
            raise HTTPException(detail="Client ID is required", status_code=400)

        if not await UserUtils.exist_client(db_session, fields.id):
            raise HTTPException(detail="Client not found", status_code=404)

        try:
            
            response = await db_session.exec(select(Client).where(Client.id == fields.id))
            client = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():

                if key in UserCrud.EXCLUDED_FIELDS_FOR_UPDATE_USER:
                    continue
                
                setattr(client, key, value)    

            db_session.add(client)
            await db_session.commit()
            
            await db_session.refresh(client)
            return client

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_client_by_email(db_session: AsyncSession, fields: ClientUpdate) -> Client:
        """Update an existing client by email."""
        
        if fields.email is None:
            raise HTTPException(detail="Client email is required", status_code=400)

        if not await UserUtils.exist_client_by_email(db_session, fields.email):
            raise HTTPException(detail="Client not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Client).where(Client.email == fields.email))
            client = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():

                if key in UserCrud.EXCLUDED_FIELDS_FOR_UPDATE_USER:
                    continue
                
                setattr(client, key, value)
            
            db_session.add(client)
            await db_session.commit()

            await db_session.refresh(client)
            return client
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def update_client_by_documentid(db_session: AsyncSession, fields: ClientUpdate) -> Client:
        """Update an existing client by document ID."""
        
        if fields.documentid is None:
            raise HTTPException(detail="Client document ID is required", status_code=400)

        if not await UserUtils.exist_client_by_documentid(db_session, fields.documentid):
            raise HTTPException(detail="Client not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Client).where(Client.documentid == fields.documentid))
            client = response.one()
            
            for key, value in fields.model_dump(exclude_unset=True).items():

                if key in UserCrud.EXCLUDED_FIELDS_FOR_UPDATE_USER:
                    continue
                    
                setattr(client, key, value)

            db_session.add(client)
            await db_session.commit()
                
            await db_session.refresh(client)
            return client
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client update failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_client(db_session: AsyncSession, client_id: int) -> bool:
        """Delete a client by ID."""
        
        # check if the client exists
        if not await UserUtils.exist_client(db_session, client_id):
            raise HTTPException(detail="Client not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Client).where(Client.id == client_id))
            
            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client deletion failed", status_code=500) from e
    
    @staticmethod
    @log_operation(True)
    async def delete_client_by_email(db_session: AsyncSession, email: str) -> bool:
        """Delete a client by email."""
        
        # check if the client exists
        if not await UserUtils.exist_client_by_email(db_session, email):
            raise HTTPException(detail="Client not found", status_code=404)

        try:
            
            response = await db_session.exec(select(Client).where(Client.email == email))
            
            await db_session.delete(response.one())
            await db_session.commit()
            
            return True
        
        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client deletion failed", status_code=500) from e
      
    @staticmethod
    @log_operation(True)
    async def delete_client_by_documentid(db_session: AsyncSession, document_id: int) -> bool:
        """Delete a client by document ID."""
        
        # check if the client exists
        if not await UserUtils.exist_client_by_documentid(db_session, document_id):
            raise HTTPException(detail="Client not found", status_code=404)
        
        try:
            
            response = await db_session.exec(select(Client).where(Client.documentid == document_id))

            await db_session.delete(response.one())
            await db_session.commit()
            
            return True

        except Exception as e:
            await db_session.rollback()
            raise HTTPException(detail="Client deletion failed", status_code=500) from e
