from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field

from .abc import BaseCreate, BaseRead, BaseUpdate


class ServiceCreate(BaseCreate):
    name: str = Field(..., description="Name of the service")
    short_description: Optional[str] = Field(None, description="Short description of the service")
    price: float = Field(..., description="Price of the service", gt=0)
    description: str = Field(..., description="Description of the service")
    cost: float = Field(..., description="Cost of the service", gt=0)

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "Ejemplo de Servicio",
                "price": 49.99,
                "description": "Descripción detallada del servicio de ejemplo.",
                "cost": 30.00,
            }
        },
    )


class ServiceUpdate(BaseUpdate):
    name: Optional[str] = Field(None, description="Name of the service")
    short_description: Optional[str] = Field(None, description="Short description of the service")
    price: Optional[float] = Field(None, description="Price of the service", gt=0)
    description: Optional[str] = Field(None, description="Description of the service")
    cost: Optional[float] = Field(None, description="Cost of the service", gt=0)

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ejemplo de Servicio",
                "short_description": "Esta es un servicio de ejemplo.",
                "price": 49.99,
                "description": "Descripción detallada del servicio de ejemplo.",
                "cost": 30.00,
                "updated_at": "2023-01-01T00:00:00Z",
            }
        },
        json_encoders={datetime: lambda v: v.isoformat()},
    )


class ServiceRead(BaseRead):
    name: str = Field(..., description="Name of the service")
    short_description: Optional[str] = Field(None, description="Short description of the service")
    price: float = Field(..., description="Price of the service")
    description: str = Field(..., description="Description of the service")
    cost: float = Field(..., description="Cost of the service")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ejemplo de Servicio",
                "short_description": "Esta es un servicio de ejemplo.",
                "price": 49.99,
                "description": "Descripción detallada del servicio de ejemplo.",
                "cost": 30.00,
            }
        },
    )
