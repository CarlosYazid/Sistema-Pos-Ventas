from fastapi import APIRouter, Depends
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import apaginate
from fastapi_querybuilder import QueryBuilder
from sqlmodel.ext.asyncio.session import AsyncSession

from core import require_scope
from db import get_session
from models import Category, ProductCategory
from schemas import CategoryCreate, CategoryRead, CategoryUpdate
from services import CategoryService, ProductCategoryService, ProductService

CATEGORY_SERVICE = CategoryService(
    product_service=ProductService(),
    product_category_service=ProductCategoryService(),
)

router = APIRouter(prefix="/category", tags=["Category"])


@router.post("/", response_model=CategoryRead)
async def create_category(
    category: CategoryCreate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await CATEGORY_SERVICE.create(category, session)


@router.get("/{category_id}", response_model=CategoryRead)
async def read_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:read")),
):

    return await CATEGORY_SERVICE.read(category_id, session)


@router.patch("/", response_model=CategoryRead)
async def update_category(
    fields: CategoryUpdate,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await CATEGORY_SERVICE.update(fields, session)


@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await CATEGORY_SERVICE.delete(category_id, session)


@router.get("/", response_model=Page[CategoryRead])
async def list_categories(
    query=QueryBuilder(Category),
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:read")),
):

    return await apaginate(session, query)


@router.post("/product", response_model=ProductCategory)
async def add_product(
    product_category: ProductCategory,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await CATEGORY_SERVICE.add_product(product_category, session)


@router.delete("/product")
async def remove_product(
    product_category: ProductCategory,
    session: AsyncSession = Depends(get_session),
    _: object = Depends(require_scope("catalog:write")),
):

    return await CATEGORY_SERVICE.remove_product(product_category, session)
