from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import require_scope
from db import get_session
from models import Service, ServiceInput
from schemas import ServiceCreate, ServiceRead, ServiceUpdate
from services import ProductService, ServiceInputService, ServiceService

router = APIRouter(prefix="/service", tags=["Service"])

SERVICE_SERVICE = ServiceService(
    product_service=ProductService(), service_input_service=ServiceInputService()
)


@router.post("/", response_model=ServiceRead)
async def create_service(
    service: ServiceCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await SERVICE_SERVICE.create(service, session)


@router.get("/{service_id}", response_model=ServiceRead)
async def read_service(
    service_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:read")),
):
    return await SERVICE_SERVICE.read(service_id, session)


@router.patch("/", response_model=ServiceRead)
async def update_service(
    fields: ServiceUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await SERVICE_SERVICE.update(fields, session)


@router.delete("/{service_id}")
async def delete_service(
    service_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await SERVICE_SERVICE.delete(service_id, session)


@router.post("/service-input", response_model=ServiceInput)
async def add_product_to_service(
    service_input: ServiceInput,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await SERVICE_SERVICE.add_product(service_input, session)


@router.delete("/service-input")
async def remove_product_from_service(
    service_input: ServiceInput,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await SERVICE_SERVICE.remove_product(service_input, session)


@router.get("/", response_model=Page[ServiceRead])
async def list_services(
    query=QueryBuilder(Service),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:all:read")),
):
    return await apaginate(session, query)
