from models import Service

from .abc import BaseRepository


class ServiceRepository(BaseRepository[Service]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Service, fields_exclude)
