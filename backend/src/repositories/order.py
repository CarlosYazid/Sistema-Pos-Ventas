from models import Order

from .abc import BaseRepository


class OrderRepository(BaseRepository[Order]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Order, fields_exclude)
