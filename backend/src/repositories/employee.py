from sqlmodel import exists, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Employee
from schemas import EmployeeProfileComplete

from .abc import UserRepository


class EmployeeRepository(UserRepository[Employee]):
    FIELDS_EXCLUDES = {
        "id",
        "created_at",
        "documentid",
        "birth_date",
    }

    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Employee, fields_exclude or EmployeeRepository.FIELDS_EXCLUDES)

    async def is_profile_completed(self, email: str, session: AsyncSession) -> bool:
        stmt = select(
            exists().where(self.model.email == email, self.model.profile_completed.is_(True))
        )

        return bool(await session.scalar(stmt))

    async def complete_profile(
        self,
        data: EmployeeProfileComplete,
        session: AsyncSession,
    ) -> Employee | None:
        employee = await self.read_by_email(data.email, session)

        employee.sqlmodel_update(data.model_dump(exclude_unset=True, exclude_none=True))

        employee.profile_completed = True

        session.add(employee)

        return employee

    async def read_by_user_id(
        self,
        user_id: str,
        session: AsyncSession,
    ) -> Employee | None:
        result = await session.exec(select(self.model).where(self.model.user_id == user_id))
        return result.one_or_none()

    async def exists_by_user_id(
        self,
        user_id: str,
        session: AsyncSession,
    ) -> bool:
        stmt = select(exists().where(self.model.user_id == user_id))

        return bool(await session.scalar(stmt))
