from models import Category

from .abc import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Category, fields_exclude)
