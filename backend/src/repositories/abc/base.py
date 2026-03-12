from typing import Type, TypeVar

from sqlalchemy import inspect
from sqlalchemy.sql.expression import Select
from sqlmodel import and_, exists, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import BaseModel
from schemas import BaseCreate, BaseUpdate

from .contracts import AT, AbstractAssociationRepository, AbstractRepository, Id

T = TypeVar("T", bound=BaseModel)


class BaseRepository(AbstractRepository[T]):
    DEFAULT_FIELD_EXCLUDE = {"id", "created_at"}

    def __init__(self, model: Type[T], fields_exclude: set[str] | None = None):
        super().__init__(model, fields_exclude or BaseRepository.DEFAULT_FIELD_EXCLUDE)

    def create(self, data: BaseCreate, session: AsyncSession) -> T:

        obj = self.model(**data.model_dump(exclude_unset=True, exclude_none=True))

        session.add(obj)

        return obj

    async def read(self, id: Id, session: AsyncSession) -> T | None:

        result = await session.exec(select(self.model).where(self.model.id == id))

        return result.one_or_none()

    async def update(self, data: BaseUpdate, session: AsyncSession) -> T | None:

        obj = await self.read(data.id, session)

        if not obj:
            return None

        payload = {
            key: value
            for key, value in data.model_dump(exclude_unset=True, exclude_none=True).items()
            if key not in self.fields_exclude
        }

        obj.sqlmodel_update(payload)

        session.add(obj)

        return obj

    async def delete(self, id: Id, session: AsyncSession) -> bool:

        obj = await self.read(id, session)

        if not obj:
            return False

        await session.delete(obj)

        return True

    async def exists(self, id: Id, session: AsyncSession) -> bool:
        return bool(await session.scalar(select(exists().where(self.model.id == id))))

    def base_query(self) -> Select:
        return select(self.model)


class BaseAssociationRepository(AbstractAssociationRepository[AT]):
    def __init__(self, model: Type[AT], fields_exclude: set[str] | None = None):
        super().__init__(model, fields_exclude)
        self._pk_columns = [column.key for column in inspect(model).primary_key]

    def add(self, criteria: AT, session: AsyncSession) -> AT:
        session.add(criteria)
        return criteria

    async def remove(self, obj: AT, session: AsyncSession) -> bool:

        result = await session.exec(select(self.model).where(self._build_identity_filter(obj)))

        obj = result.one_or_none()

        if not obj:
            return False

        await session.delete(obj)
        return True

    async def exists(self, obj: AT, session: AsyncSession) -> bool:

        stmt = select(exists().where(self._build_identity_filter(obj)))

        return bool(await session.scalar(stmt))

    def _build_identity_filter(self, obj: AT):
        return and_(
            *[getattr(self.model, field) == getattr(obj, field) for field in self._pk_columns]
        )
