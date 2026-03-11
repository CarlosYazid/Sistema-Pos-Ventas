from typing import Protocol

from .base import BaseBase, BaseCreate, BaseRead, BaseUpdate
from .user import UserBase, UserCreate, UserRead, UserUpdate

__all__ = [
    "AbstractCreate",
    "AbstractRead",
    "AbstractUpdate",
    "BaseBase",
    "BaseCreate",
    "BaseRead",
    "BaseUpdate",
    "UserBase",
    "UserCreate",
    "UserRead",
    "UserUpdate",
]


class AbstractCreate(Protocol):
    pass


class AbstractRead(Protocol):
    pass


class AbstractUpdate(Protocol):
    pass
