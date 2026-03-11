from abc import ABC, abstractmethod
from typing import Generic, Type, TypeVar

from db import AbstractSession
from models import AbstractModel
from schemas import AbstractCreate, AbstractUpdate

AT = TypeVar("AT", bound=AbstractModel)

Id = int
Criteria = Id | AT


class AbstractRepository(ABC, Generic[AT]):
    def __init__(
        self,
        model: Type[AT],
        fields_exclude: set[str] | None = None,
    ):
        self.model = model
        self.fields_exclude = fields_exclude

    @abstractmethod
    def create(
        self,
        data: AbstractCreate,
        session: AbstractSession,
    ) -> AT: ...

    @abstractmethod
    async def read(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> AT | None: ...

    @abstractmethod
    async def update(
        self,
        data: AbstractUpdate,
        session: AbstractSession,
    ) -> AT | None: ...

    @abstractmethod
    async def delete(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> bool: ...

    @abstractmethod
    async def exists(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> bool: ...


class AbstractAssociationRepository(ABC, Generic[AT]):
    def __init__(
        self,
        model: Type[AT],
        fields_exclude: set[str] | None = None,
    ):
        self.model = model
        self.fields_exclude = fields_exclude

    @abstractmethod
    def add(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> AT: ...

    @abstractmethod
    async def remove(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> bool: ...

    @abstractmethod
    async def exists(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> bool: ...
