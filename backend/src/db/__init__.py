from typing import Protocol

from .main import close_engine, get_session, init_db, init_engine

__all__ = ["AbstractSession", "get_session", "init_db", "init_engine", "close_engine"]


class AbstractSession(Protocol):
    pass
