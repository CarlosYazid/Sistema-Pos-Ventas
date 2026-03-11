from typing import Protocol

from .base import BaseModel
from .user import UserModel

__all__ = ["AbstractModel", "BaseModel", "UserModel"]


class AbstractModel(Protocol):
    pass
