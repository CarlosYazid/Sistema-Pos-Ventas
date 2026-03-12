from fastapi import APIRouter

from .routes import (
    ClientRouter,
    EmployeeRouter,
    FileRouter,
    OrderRouter,
    PaymentRouter,
    ProductRouter,
    ServiceRouter,
)

router = APIRouter(tags=["v1"])

router.include_router(ClientRouter)
router.include_router(EmployeeRouter)
router.include_router(ProductRouter)
router.include_router(ServiceRouter)
router.include_router(OrderRouter)
router.include_router(PaymentRouter)
router.include_router(FileRouter)
