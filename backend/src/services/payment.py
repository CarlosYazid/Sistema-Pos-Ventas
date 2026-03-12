from repositories import PaymentRepository

from .abc import BaseService


class PaymentService(BaseService[PaymentRepository]):
    def __init__(self, fields_exclude: set[str] | None = None):
        super().__init__(PaymentRepository(fields_exclude))
