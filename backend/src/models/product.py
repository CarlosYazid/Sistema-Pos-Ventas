from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlmodel import Field, Relationship, SQLModel

from .abc import BaseModel
from .service import ServiceInput

if TYPE_CHECKING:
    from .order import OrderProduct
    from .service import Service


class ProductCategory(SQLModel, table=True):
    __table_args__ = (Index("ix_pc_category_id", "category_id"),)

    product_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("product.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

    category_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("category.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )


class Product(BaseModel, table=True):
    """
    Product model for the database.
    """

    name: str = Field(..., description="Product's name")
    short_description: Optional[str] = Field(None, description="Short description of the product")
    price: float = Field(..., description="Product's price")
    cost: float = Field(..., description="Product's cost")
    stock: int = Field(..., description="Available stock of the product")
    minimum_stock: int = Field(..., description="Minimum stock level of the product")
    image_key: Optional[str] = Field(None, description="Key of the product image")
    expiration_date: Optional[date] = Field(
        None, description="Expiration date of the consumable product"
    )

    services: list["Service"] = Relationship(
        back_populates="products",
        link_model=ServiceInput,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "passive_deletes": True,
        },
    )

    categories: list["Category"] = Relationship(
        back_populates="products",
        link_model=ProductCategory,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "passive_deletes": True,
        },
    )

    order_products: Optional[list["OrderProduct"]] = Relationship(
        back_populates="product", sa_relationship_kwargs={"lazy": "selectin"}
    )


class Category(BaseModel, table=True):
    """
    Category model for the database.
    """

    name: str = Field(..., description="Category's name")
    description: str = Field(..., description="Category's description")

    products: list["Product"] = Relationship(
        back_populates="categories",
        link_model=ProductCategory,
        sa_relationship_kwargs={"lazy": "selectin", "passive_deletes": True},
    )
