from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import ConfigDict
from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship, SQLModel

from .abc import BaseModel

if TYPE_CHECKING:
    from .client import Client
    from .employee import Employee
    from .product import Product
    from .service import Service


class OrderProduct(SQLModel, table=True):
    """
    Model for products in an order.
    """

    order_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("order.id", ondelete="CASCADE"),
            primary_key=True,
            index=True,
        )
    )

    product_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("product.id"),
            primary_key=True,
            index=True,
        )
    )

    quantity: int = Field(..., description="Quantity of the product")

    order: "Order" = Relationship(back_populates="order_products")
    product: "Product" = Relationship(back_populates="order_products")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"example": {"order_id": 1, "product_id": 1, "quantity": 2}},
    )


class OrderService(SQLModel, table=True):
    """
    Model for services in an order.
    """

    order_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("order.id", ondelete="CASCADE"),
            primary_key=True,
            index=True,
        )
    )

    service_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("service.id"),
            primary_key=True,
            index=True,
        )
    )

    quantity: int = Field(..., description="Quantity of the service")

    order: "Order" = Relationship(back_populates="order_services")
    service: "Service" = Relationship(back_populates="order_services")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={"example": {"order_id": 1, "service_id": 1, "quantity": 2}},
    )


class OrderStatus(str, Enum):
    """
    Enum for order statuses.
    """

    PENDING = "Pendiente"
    COMPLETED = "Completada"
    CANCELLED = "Cancelada"


class Order(BaseModel, table=True):
    """
    Model for orders.
    """

    client_id: int = Field(
        foreign_key="client.id", description="Client who placed the order", index=True
    )

    total_price: Optional[float] = Field(..., description="Total price of the order")

    status: OrderStatus = Field(
        default=OrderStatus.PENDING, description="Current status of the order"
    )

    employee_id: int = Field(
        foreign_key="employee.id", description="Employee assigned to the order", index=True
    )

    order_products: Optional[list["OrderProduct"]] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    order_services: Optional[list["OrderService"]] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    client: "Client" = Relationship(
        back_populates="orders", sa_relationship_kwargs={"lazy": "selectin"}
    )

    employee: "Employee" = Relationship(
        back_populates="orders", sa_relationship_kwargs={"lazy": "selectin"}
    )
