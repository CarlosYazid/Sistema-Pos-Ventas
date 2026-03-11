from models import Client

from .abc import UserRepository


class ClientRepository(UserRepository[Client]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Client, fields_exclude)
