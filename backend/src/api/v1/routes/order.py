from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import require_scope
from db import get_session
from models import Order, OrderProduct
from models import OrderService as OrderServiceModel
from schemas import OrderCreate, OrderRead, OrderUpdate
from services import (
    InventoryService,
    InvoiceService,
    OrderProductService,
    OrderService,
    OrderServiceService,
    ProductService,
    ServiceInputService,
    ServiceService,
)

router = APIRouter(prefix="/order", tags=["Order"])

PRODUCT_SERVICE = ProductService()
ORDER_SERVICE = OrderService(
    product_service=PRODUCT_SERVICE,
    service_service=ServiceService(
        product_service=PRODUCT_SERVICE, service_input_service=ServiceInputService()
    ),
    order_product_service=OrderProductService(),
    order_service_service=OrderServiceService(),
)

INVENTORY_SERVICE = InventoryService(order_service=ORDER_SERVICE)

INVOICE_SERVICE = InvoiceService()


@router.post("/", response_model=OrderRead)
async def create_order(
    order: OrderCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.create(order, session)


@router.get("/{order_id}", response_model=OrderRead)
async def read_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:read")),
):

    return await ORDER_SERVICE.read(order_id, session)


@router.patch("/", response_model=OrderRead)
async def update_order(
    fields: OrderUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.update(fields, session)


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.delete(order_id, session)


@router.post("/product", response_model=OrderProduct)
async def add_product(
    order_product: OrderProduct,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.add_product(order_product, session)


@router.patch("/product", response_model=OrderProduct)
async def update_quantity_product(
    order_product: OrderProduct,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.update_quantity_product(order_product, session)


@router.delete("/product")
async def remove_product(
    order_product: OrderProduct,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.remove_product(order_product, session)


@router.post("/service", response_model=OrderServiceModel)
async def add_service(
    order_service: OrderServiceModel,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.add_service(order_service, session)


@router.patch("/service", response_model=OrderServiceModel)
async def update_quantity_service(
    order_service: OrderServiceModel,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.update_quantity_service(order_service, session)


@router.delete("/service")
async def remove_service(
    order_service: OrderServiceModel,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:write")),
):

    return await ORDER_SERVICE.remove_service(order_service, session)


@router.get("/", response_model=Page[OrderRead])
async def list_orders(
    query=QueryBuilder(Order),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("orders:read")),
):

    return await apaginate(session, query)


@router.patch("/{order_id}/inventory", response_model=OrderRead)
async def update_inventory(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("inventory:write")),
):

    return await INVENTORY_SERVICE.update_inventory(order_id, session)


@router.post("/{order_id}/invoice")
async def generate_invoice(_: object = Depends(require_scope("invoices:write"))):
    pass
