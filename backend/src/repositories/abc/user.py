from typing import Type, TypeVar

from pydantic import EmailStr
from sqlmodel import exists, select
from sqlmodel.ext.asyncio.session import AsyncSession

from models import UserModel
from schemas import UserUpdate

from .base import BaseRepository
from .contracts import Id

T = TypeVar("T", bound=UserModel)

type Email = EmailStr
type DocumentId = int


class UserRepository(BaseRepository[T]):
    FIELDS_EXCLUDES = {"id", "created_at", "documentid"}

    def __init__(self, model: Type[T], fields_exclude: set[str] | None = None):
        super().__init__(model, fields_exclude or UserRepository.FIELDS_EXCLUDES)

    # ---------- READ ----------

    async def read_by_email(self, email: Email, session: AsyncSession) -> T | None:
        result = await session.exec(select(self.model).where(self.model.email == email))

        return result.one_or_none()

    async def read_by_documentid(self, documentid: DocumentId, session: AsyncSession) -> T | None:
        result = await session.exec(select(self.model).where(self.model.documentid == documentid))

        return result.one_or_none()

    # ---------- UPDATE ----------

    async def update_by_email(
        self, email: Email, data: UserUpdate, session: AsyncSession
    ) -> T | None:
        return self._update_obj(await self.read_by_email(email, session), data, session)

    async def update_by_documentid(
        self, documentid: DocumentId, data: UserUpdate, session: AsyncSession
    ) -> T | None:
        return self._update_obj(await self.read_by_documentid(documentid, session), data, session)

    # ---------- DELETE ----------

    async def delete_by_email(self, email: Email, session: AsyncSession) -> bool:
        return await self._delete_obj(await self.read_by_email(email, session), session)

    async def delete_by_documentid(self, documentid: DocumentId, session: AsyncSession) -> bool:
        return await self._delete_obj(await self.read_by_documentid(documentid, session), session)

    # ------ Soft Delete -------

    async def soft_delete(self, id: Id, session: AsyncSession) -> bool:
        return self._soft_delete(await self.read(id, session), session)

    async def soft_delete_by_email(self, email: Email, session: AsyncSession) -> bool:
        return self._soft_delete(await self.read_by_email(email, session), session)

    async def soft_delete_by_documentid(
        self, documentid: DocumentId, session: AsyncSession
    ) -> bool:
        return await self._soft_delete(await self.read_by_documentid(documentid, session), session)

    # ---------- EXIST ----------

    async def exists_by_email(self, email: Email, session: AsyncSession) -> bool:
        return bool(await session.scalar(select(exists().where(self.model.email == email))))

    async def exists_by_documentid(self, documentid: DocumentId, session: AsyncSession) -> bool:
        return bool(
            await session.scalar(select(exists().where(self.model.documentid == documentid)))
        )

    def _soft_delete(self, user: T | None, session: AsyncSession) -> bool:
        if not user:
            return False

        user.status = False
        session.add(user)

        return True
