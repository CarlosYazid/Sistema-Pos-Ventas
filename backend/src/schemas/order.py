from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from models import OrderStatus

from .abc import BaseCreate, BaseRead, BaseUpdate


class OrderCreate(BaseCreate):
    client_id: int = Field(..., description="User who placed the order", gt=0)
    total_price: Optional[float] = Field(None, description="Total price of the order", gt=0)
    status: OrderStatus = Field(
        default=OrderStatus.PENDING, description="Current status of the order"
    )
    employee_id: int = Field(..., description="Employee assigned to the order", gt=0)

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "client_id": 1,
                "total_price": 59.99,
                "status": "Pendiente",
                "employee_id": 1,
            }
        },
    )


class OrderUpdate(BaseUpdate):
    total_price: Optional[float] = Field(None, description="Total price of the order", gt=0)
    status: Optional[OrderStatus] = Field(None, description="Current status of the order")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "total_price": 3.5,
                "status": "Completada",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        },
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class OrderRead(BaseRead):
    client_id: int = Field(..., description="User who placed the order")
    total_price: Optional[float] = Field(None, description="Total price of the order")
    status: OrderStatus = Field(..., description="Current status of the order")
    employee_id: int = Field(..., description="Employee assigned to the order")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "client_id": 1,
                "total_price": 59.99,
                "status": "Pendiente",
                "employee_id": 1,
            }
        },
    )
