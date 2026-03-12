from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core.errors import (
    EmployeeProfileAlreadyCompletedError,
    MissingFieldError,
    NotFoundError,
    UpdateError,
)
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
        if not data.email and not data.user_id:
            raise MissingFieldError("user_id and email")

        if not await self.repository.exists_by_email(
            data.email, session
        ) and not await self.repository.exist_by_user_id(data.user_id, session):
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
