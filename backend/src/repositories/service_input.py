from models import ServiceInput
from repositories.abc import BaseAssociationRepository


class ServiceInputRepository(BaseAssociationRepository[ServiceInput]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(ServiceInput, fields_exclude)
