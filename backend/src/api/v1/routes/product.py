from botocore.client import BaseClient
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import get_e2_client, require_scope
from db import get_session
from models import Product
from schemas import (
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from services import ProductImageService, ProductService
from utils import ProductUtils

router = APIRouter(prefix="/product", tags=["Product"])

PRODUCT_SERVICE = ProductService()

PRODUCT_IMAGE_SERVICE = ProductImageService(product_service=PRODUCT_SERVICE, utils=ProductUtils())


@router.post("/", response_model=ProductRead)
async def create_product(
    product: ProductCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await PRODUCT_SERVICE.create(product, session)


@router.get("/{product_id}", response_model=ProductRead)
async def read_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:read")),
):

    return await PRODUCT_SERVICE.read(product_id, session)


@router.patch("/", response_model=ProductRead)
async def update_product(
    fields: ProductUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await PRODUCT_SERVICE.update(fields, session)


@router.patch("/image/{product_id}", response_model=ProductRead)
async def update_product_image(
    product_id: int,
    image: UploadFile = File(..., title="photo_product"),
    storage_client: BaseClient = Depends(get_e2_client),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await PRODUCT_IMAGE_SERVICE.update_image(product_id, image, session, storage_client)


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await PRODUCT_SERVICE.delete(product_id, session)


@router.get("/", response_model=Page[ProductRead])
async def list_products(
    query=QueryBuilder(Product),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:read")),
):

    return await apaginate(session, query)


@router.get("/low-stock", response_model=Page[ProductRead])
async def search_low_stock_products(
    session: AsyncSession = Depends(get_session), _: object = Depends(require_scope("catalog:read"))
):

    return await apaginate(session, PRODUCT_SERVICE.search_low_stock_products())


@router.get("/expired", response_model=Page[ProductRead])
async def search_expired_products(
    session: AsyncSession = Depends(get_session), _: object = Depends(require_scope("catalog:read"))
):

    return await apaginate(session, PRODUCT_SERVICE.search_expired_products())
