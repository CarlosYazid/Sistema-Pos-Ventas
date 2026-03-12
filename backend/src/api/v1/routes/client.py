from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import require_scope
from db import get_session
from models import Client
from schemas import ClientCreate, ClientRead, ClientUpdate
from services import ClientService

router = APIRouter(prefix="/client", tags=["Client"])

CLIENT_SERVICE = ClientService()


@router.post("/", response_model=ClientRead)
async def create_client(
    client: ClientCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("clients:write")),
):

    return await CLIENT_SERVICE.create(client, session)


@router.get("/{client_id}", response_model=ClientRead)
async def read_client(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("clients:read")),
):

    return await CLIENT_SERVICE.read(client_id, session)


@router.patch("/", response_model=ClientRead)
async def update_client(
    fields: ClientUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("clients:write")),
):

    return await CLIENT_SERVICE.update(fields, session)


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("clients:write")),
):

    return await CLIENT_SERVICE.delete(client_id, session)


@router.get("/", response_model=Page[ClientRead])
async def list_clients(
    query=QueryBuilder(Client),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("clients:all:read")),
):

    return await apaginate(session, query)
