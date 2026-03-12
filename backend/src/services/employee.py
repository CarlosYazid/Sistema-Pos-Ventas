from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core.errors import (
    EmployeeProfileAlreadyCompletedError,
    UpdateError,
)
from models import Employee
from repositories import EmployeeRepository
from schemas import EmployeeProfileComplete

from .abc import UserService


class EmployeeService(UserService[EmployeeRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(EmployeeRepository(fields_exclude))

    async def update_email(self, email: str, employee: Employee, session: AsyncSession):

        try:
            employee.sqlmodel_update({"email": email})
            employee.profile_completed = True

            session.add(employee)
            await session.commit()
            await session.refresh(employee)

            return employee

        except SQLAlchemyError as e:
            await session.rollback()
            raise UpdateError(self.entity) from e

    async def complete_profile(
        self, data: EmployeeProfileComplete, employee: Employee, session: AsyncSession
    ):

        if employee.profile_completed:
            raise EmployeeProfileAlreadyCompletedError(data.first_name)

        try:
            employee.sqlmodel_update(data.model_dump(exclude_unset=True, exclude_none=True))
            employee.profile_completed = True

            session.add(employee)
            await session.commit()
            await session.refresh(employee)

            return employee

        except SQLAlchemyError as e:
            await session.rollback()
            raise UpdateError(self.entity) from e
