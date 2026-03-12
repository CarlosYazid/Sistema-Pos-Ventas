from typing import Generic, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.errors import (
    CreationError,
    DeletionError,
    EntityAlreadyExistsError,
    MissingFieldError,
    NotFoundError,
    ReadingError,
    UpdateError,
)
from models import BaseModel
from repositories import BaseAssociationRepository, BaseRepository
from schemas import BaseCreate, BaseUpdate

from .contracts import AbstractAssociationService, AbstractService

Repository = TypeVar("Repository", bound=BaseRepository[BaseModel])
AssociationRepository = TypeVar("AssociationRepository", bound=BaseAssociationRepository[SQLModel])


class BaseService(AbstractService[BaseModel], Generic[Repository]):
    def __init__(self, repository: Repository):
        super().__init__(repository)

    async def create(self, data: BaseCreate, session: AsyncSession) -> BaseModel:

        try:
            entity = self.repository.create(data, session)

            await session.commit()
            await session.refresh(entity)

            return entity

        except SQLAlchemyError as e:
            await session.rollback()
            raise CreationError(self.entity) from e

    async def read(self, criteria: int, session: AsyncSession) -> BaseModel:
        try:
            entity = await self.repository.read(criteria, session)
            if entity is None:
                raise NotFoundError(self.entity)
            return entity
        except SQLAlchemyError as e:
            raise ReadingError(self.entity) from e

    async def update(self, data: BaseUpdate, session: AsyncSession) -> BaseModel:

        if data.id is None:
            raise MissingFieldError("id")

        if not await self.exists(data.id, session):
            raise NotFoundError(self.entity)

        try:
            entity = await self.repository.update(data, session)
            await session.commit()
            await session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            await session.rollback()
            raise UpdateError(self.entity) from e

    async def delete(self, criteria: int, session: AsyncSession) -> bool:
        if not await self.exists(criteria, session):
            raise NotFoundError(self.entity)

        try:
            result = await self.repository.delete(criteria, session)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            await session.rollback()
            raise DeletionError(self.entity) from e

    async def exists(self, criteria: int, session: AsyncSession) -> bool:
        return await self.repository.exists(criteria, session)


class BaseAssociationService(AbstractAssociationService[SQLModel], Generic[AssociationRepository]):
    def __init__(self, repository: AssociationRepository):
        super().__init__(repository)

    async def add(self, data: SQLModel, session: AsyncSession) -> SQLModel:

        if await self.exists(data, session):
            raise EntityAlreadyExistsError(self.entity)

        try:
            entity = await self.repository.add(data, session)
            await session.commit()
            await session.refresh(entity)
            return entity
        except SQLAlchemyError as e:
            await session.rollback()
            raise CreationError(self.entity) from e

    async def remove(self, data: SQLModel, session: AsyncSession) -> bool:

        if not await self.exists(data, session):
            raise NotFoundError(self.entity)
        try:
            return await self.repository.remove(data, session)
        except SQLAlchemyError as e:
            await session.rollback()
            raise DeletionError(self.entity) from e

    async def exists(self, data: SQLModel, session: AsyncSession) -> bool:
        return await self.repository.exists(data, session)
