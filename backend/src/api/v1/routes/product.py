from botocore.client import BaseClient
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import get_e2_client, require_scope
from db import get_session
from models import Category, Product, ProductCategory
from schemas import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from services import CategoryService, ProductCategoryService, ProductImageService, ProductService
from utils import ProductUtils

router = APIRouter(prefix="/product", tags=["Product"])

PRODUCT_SERVICE = ProductService()
CATEGORY_SERVICE = CategoryService(
    product_service=PRODUCT_SERVICE,
    product_category_service=ProductCategoryService(),
)
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
    _: object = Depends(require_scope("catalog:all:read")),
):
    return await apaginate(session, query)


@router.post("/product-category", response_model=ProductCategory)
async def add_product_to_category(
    product_category: ProductCategory,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await CATEGORY_SERVICE.add_product(product_category, session)


@router.delete("/product-category")
async def remove_product_from_category(
    product_category: ProductCategory,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await CATEGORY_SERVICE.remove_product(product_category, session)


@router.post("/category", response_model=CategoryRead)
async def create_category(
    category: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await CATEGORY_SERVICE.create(category, session)


@router.get("/category/{category_id}", response_model=CategoryRead)
async def read_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:read")),
):
    return await CATEGORY_SERVICE.read(category_id, session)


@router.patch("/category", response_model=CategoryRead)
async def update_category(
    fields: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await CATEGORY_SERVICE.update(fields, session)


@router.delete("/category/{category_id}")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):
    return await CATEGORY_SERVICE.delete(category_id, session)


@router.get("/category", response_model=Page[CategoryRead])
async def list_categories(
    query=QueryBuilder(Category),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:all:read")),
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
