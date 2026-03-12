from typing import Type, TypeVar

from sqlmodel.ext.asyncio.session import AsyncSession

from models import UserModel

from .base import BaseRepository
from .contracts import Id

T = TypeVar("T", bound=UserModel)


class UserRepository(BaseRepository[T]):
    FIELDS_EXCLUDES = {"id", "created_at", "documentid"}

    def __init__(self, model: Type[T], fields_exclude: set[str] | None = None):
        super().__init__(model, fields_exclude or UserRepository.FIELDS_EXCLUDES)

    # ------ Soft Delete -------

    async def soft_delete(self, id: Id, session: AsyncSession) -> bool:
        return self._soft_delete(await self.read(id, session), session)

    def _soft_delete(self, user: T | None, session: AsyncSession) -> bool:
        if not user:
            return False

        user.status = False
        session.add(user)

        return True
