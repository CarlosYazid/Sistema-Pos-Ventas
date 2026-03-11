from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core import (
    EmployeeProfileAlreadyCompletedError,
    MissingFieldError,
    NotFoundError,
    ReadingError,
    UpdateError,
)
from models import Employee
from repositories import EmployeeRepository
from schemas import EmployeeProfileComplete

from .abc import UserService


class EmployeeService(UserService[EmployeeRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(EmployeeRepository(fields_exclude))

    async def complete_profile(
        self,
        data: EmployeeProfileComplete,
        session: AsyncSession,
    ):
        if not data.email:
            raise MissingFieldError("email")

        if not await self.repository.exists_by_email(data.email, session):
            raise NotFoundError(self.entity)

        if await self.repository.is_profile_completed(data.email, session):
            raise EmployeeProfileAlreadyCompletedError(data.email)

        try:
            employee = await self.repository.complete_profile(data, session)

            await session.commit()
            await session.refresh(employee)

            return employee

        except SQLAlchemyError as e:
            await session.rollback()
            raise UpdateError(self.entity) from e

    async def read_by_user_id(self, user_id: str, session: AsyncSession):
        if not user_id:
            raise MissingFieldError("user_id")

        try:
            employee = await self.repository.read_by_user_id(user_id, session)
            if employee is None:
                raise NotFoundError(self.entity)
            return employee
        except SQLAlchemyError as e:
            raise ReadingError(self.entity) from e

    async def exists_by_user_id(self, user_id: str, session: AsyncSession) -> bool:
        if not user_id:
            raise MissingFieldError("user_id")

        return await self.repository.exists_by_user_id(user_id, session)

    async def sync_identity_by_user_id(
        self,
        *,
        user_id: str,
        email: str,
        session: AsyncSession,
    ) -> Employee:
        if not user_id:
            raise MissingFieldError("user_id")
        if not email:
            raise MissingFieldError("email")

        try:
            employee = await self.repository.read_by_user_id(user_id, session)

            if employee is None:
                employee = await self.repository.read_by_email(email, session)

            if employee is None:
                employee = Employee(user_id=user_id, email=email)
            else:
                employee.user_id = user_id
                employee.email = email

            session.add(employee)
            await session.commit()
            await session.refresh(employee)

            return employee

        except SQLAlchemyError as e:
            await session.rollback()
            raise UpdateError(self.entity) from e
