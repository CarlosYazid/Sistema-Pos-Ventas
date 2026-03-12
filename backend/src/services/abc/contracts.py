from abc import ABC, abstractmethod
from typing import Generic

from db import AbstractSession
from repositories.abc import AT, Criteria
from repositories.abc.contracts import AbstractAssociationRepository, AbstractRepository
from schemas import AbstractCreate, AbstractUpdate


class AbstractService(ABC, Generic[AT]):
    def __init__(self, repository: AbstractRepository[AT]):
        self.repository = repository
        self.entity = repository.model.__name__

    @abstractmethod
    async def create(
        self,
        data: AbstractCreate,
        session: AbstractSession,
    ) -> AT: ...

    @abstractmethod
    async def read(
        self,
        criteria: Criteria,
        session: AbstractSession,
    ) -> AT: ...

    @abstractmethod
    async def update(
        self,
        data: AbstractUpdate,
        session: AbstractSession,
    ) -> AT: ...

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


class AbstractAssociationService(ABC, Generic[AT]):
    def __init__(self, repository: AbstractAssociationRepository[AT]):
        self.repository = repository
        self.entity = repository.model.__name__

    @abstractmethod
    async def add(
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
