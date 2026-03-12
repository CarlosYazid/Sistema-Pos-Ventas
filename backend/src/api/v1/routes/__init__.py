from .client import router as ClientRouter
from .employee import router as EmployeeRouter
from .files import router as FileRouter
from .order import router as OrderRouter
from .payment import router as PaymentRouter
from .product import router as ProductRouter
from .service import router as ServiceRouter

__all__ = [
    "FileRouter",
    "OrderRouter",
    "OthersRouter",
    "ProductRouter",
    "ServiceRouter",
    "ClientRouter",
    "PaymentRouter",
    "EmployeeRouter",
]
