from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core.errors import DeletionError, NotFoundError
from models import UserModel
from repositories import UserRepository

from .base import BaseService

Repository = TypeVar("Repository", bound=UserRepository[UserModel])


class UserService(BaseService[Repository]):
    def __init__(self, repository: Repository):
        super().__init__(repository)

    async def soft_delete(self, id: int, session: AsyncSession) -> bool:
        if not await self.repository.exists(id, session):
            raise NotFoundError(self.entity)

        try:
            return await self.repository.soft_delete(id, session)

        except SQLAlchemyError as e:
            await session.rollback()

            raise DeletionError(self.entity) from e
