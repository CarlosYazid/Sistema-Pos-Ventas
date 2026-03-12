from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from core import require_scope
from db import get_session
from schemas import PaymentCreate, PaymentRead, PaymentUpdate
from services import PaymentService

router = APIRouter(prefix="/payment", tags=["Payment"])

PAYMENT_SERVICE = PaymentService()


@router.post("/", response_model=PaymentRead)
async def create_payment(
    payment: PaymentCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("payments:write")),
):

    return await PAYMENT_SERVICE.create(payment, session)


@router.get("/{payment_id}", response_model=PaymentRead)
async def read_payment(
    payment_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("payments:read")),
):

    return await PAYMENT_SERVICE.read(payment_id, session)


@router.patch("/", response_model=PaymentRead)
async def update_payment(
    fields: PaymentUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("payments:write")),
):

    return await PAYMENT_SERVICE.update(fields, session)


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("payments:write")),
):

    return await PAYMENT_SERVICE.delete(payment_id, session)
