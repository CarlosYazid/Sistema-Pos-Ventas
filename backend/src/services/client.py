from repositories import ClientRepository

from .abc import UserService


class ClientService(UserService[ClientRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(ClientRepository(fields_exclude))
