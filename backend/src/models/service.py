from typing import TYPE_CHECKING, Optional

from pydantic import ConfigDict
from sqlalchemy import Column, ForeignKey, Index, Integer
from sqlmodel import Field, Relationship, SQLModel

from .abc import BaseModel

if TYPE_CHECKING:
    from .order import OrderService
    from .product import Product


class ServiceInput(SQLModel, table=True):
    """
    Relation between Service and Product.
    """

    __table_args__ = (Index("ix_si_product_id", "product_id"),)

    service_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("service.id", ondelete="CASCADE"),
            primary_key=True,
        )
    )

    product_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("product.id", ondelete="RESTRICT"),
            primary_key=True,
        )
    )

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True, json_schema_extra={"example": {"service_id": 1, "product_id": 1}}
    )


class Service(BaseModel, table=True):
    """
    Service model for the database.
    """

    name: str = Field(..., description="Name of the service")
    short_description: Optional[str] = Field(None, description="Short description of the service")
    price: float = Field(..., description="Price of the service")
    description: str = Field(..., description="Description of the service")
    cost: float = Field(..., description="Cost of the service")

    products: list["Product"] = Relationship(
        back_populates="services",
        link_model=ServiceInput,
        sa_relationship_kwargs={
            "lazy": "selectin",
            "passive_deletes": True,
        },
    )

    order_services: Optional[list["OrderService"]] = Relationship(
        back_populates="service", sa_relationship_kwargs={"lazy": "selectin"}
    )
