from repositories import ServiceInputRepository

from .abc import BaseAssociationService


class ServiceInputService(BaseAssociationService[ServiceInputRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(ServiceInputRepository(fields_exclude))
