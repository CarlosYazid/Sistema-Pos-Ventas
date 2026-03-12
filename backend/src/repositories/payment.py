from models import Payment

from .abc import BaseRepository


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(Payment, fields_exclude)
