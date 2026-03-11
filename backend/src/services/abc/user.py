from typing import TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel.ext.asyncio.session import AsyncSession

from core import DeletionError, MissingFieldError, NotFoundError, ReadingError, UpdateError
from repositories import UserRepository
from schemas import UserUpdate

from .base import BaseService

Repository = TypeVar("Repository", bound=UserRepository)


class UserService(BaseService[Repository]):
    def __init__(self, repository: Repository):
        super().__init__(repository)

    async def read_by_email(self, email: str, session: AsyncSession):
        try:
            user = await self.repository.read_by_email(email, session)

            if user is None:
                raise NotFoundError(self.entity)

            return user

        except SQLAlchemyError as e:
            raise ReadingError(self.entity) from e

    async def read_by_documentid(self, documentid: int, session: AsyncSession):
        try:
            user = await self.repository.read_by_documentid(documentid, session)

            if user is None:
                raise NotFoundError(self.entity)

            return user

        except SQLAlchemyError as e:
            raise ReadingError(self.entity) from e

    async def update_by_email(self, data: UserUpdate, session: AsyncSession):
        if data.email is None:
            raise MissingFieldError("email")

        if not await self.repository.exists_by_email(data.email, session):
            raise NotFoundError(self.entity)

        try:
            user = await self.repository.update_by_email(data.email, data, session)

            await session.commit()
            await session.refresh(user)

            return user

        except SQLAlchemyError as e:
            await session.rollback()

            raise UpdateError(self.entity) from e

    async def update_by_documentid(self, data: UserUpdate, session: AsyncSession):
        if data.documentid is None:
            raise MissingFieldError("documentid")

        if not await self.repository.exist_by_documentid(data.documentid, session):
            raise NotFoundError(self.entity)

        try:
            user = await self.repository.update_by_documentid(data.documentid, data, session)

            await session.commit()
            await session.refresh(user)

            return user

        except SQLAlchemyError as e:
            await session.rollback()

            raise UpdateError(self.entity) from e

    async def delete_by_email(self, email: str, session: AsyncSession) -> bool:
        if not await self.repository.exists_by_email(email, session):
            raise NotFoundError(self.entity)

        try:
            return await self.repository.delete_by_email(id, session)

        except SQLAlchemyError as e:
            await session.rollback()

            raise DeletionError(self.entity) from e

    async def delete_by_documentid(self, documentid: int, session: AsyncSession) -> bool:
        if not await self.repository.exists_by_documentid(documentid, session):
            raise NotFoundError(self.entity)

        try:
            return await self.repository.delete_by_documentid(documentid, session)

        except SQLAlchemyError as e:
            await session.rollback()

            raise DeletionError(self.entity) from e

    async def soft_delete(self, id: int, session: AsyncSession) -> bool:
        if not await self.repository.exist(id, session):
            raise NotFoundError(self.entity)

        try:
            return await self.repository.soft_delete(id, session)

        except SQLAlchemyError as e:
            await session.rollback()

            raise DeletionError(self.entity) from e

    async def soft_delete_by_email(self, email: str, session: AsyncSession) -> bool:
        if not await self.repository.exists_by_email(email, session):
            raise NotFoundError(self.entity)

        try:
            return await self.repository.soft_delete_by_email(email, session)

        except SQLAlchemyError as e:
            await session.rollback()

            raise DeletionError(self.entity) from e

    async def soft_delete_by_documentid(self, documentid: int, session: AsyncSession) -> bool:
        if not await self.repository.exists_by_documentid(documentid, session):
            raise NotFoundError(self.entity)

        try:
            return await self.repository.soft_delete_by_documentid(documentid, session)

        except SQLAlchemyError as e:
            await session.rollback()

            raise DeletionError(self.entity) from e
