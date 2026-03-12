from datetime import date, datetime
from typing import Optional

from pydantic import ConfigDict, Field

from .abc import BaseCreate, BaseRead, BaseUpdate


class ProductCreate(BaseCreate):
    name: str = Field(..., description="Product's name")
    short_description: Optional[str] = Field(None, description="Short description of the product")
    price: float = Field(..., description="Product's price", gt=0)
    cost: float = Field(..., description="Product's cost", gt=0)
    stock: int = Field(..., description="Available stock of the product", gt=0)
    minimum_stock: int = Field(..., description="Minimum stock level of the product", gt=0)
    expiration_date: Optional[date] = Field(
        None, description="Expiration date of the consumable product"
    )

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "name": "Ejemplo de producto de papelería",
                "short_description": "Este es un producto de papelería de ejemplo.",
                "price": 9.99,
                "stock": 50,
                "cost": 5.6,
                "minimum_stock": 7,
                "expiration_date": "2023-12-31",
            }
        },
        json_encoders={date: lambda v: v.isoformat()},
    )


class ProductRead(BaseRead):
    """
    Product model for the API response.
    """

    name: str = Field(..., description="Product's name")
    short_description: Optional[str] = Field(None, description="Short description of the product")
    price: float = Field(..., description="Product's price")
    cost: float = Field(..., description="Product's cost")
    stock: int = Field(..., description="Available stock of the product")
    minimum_stock: int = Field(..., description="Minimum stock level of the product")
    image_key: Optional[str] = Field(None, description="URL of the product image")
    expiration_date: Optional[date] = Field(
        None, description="Expiration date of the consumable product"
    )

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ejemplo de producto de papelería",
                "short_description": "Este es un producto de papelería de ejemplo.",
                "price": 9.99,
                "stock": 50,
                "minimum_stock": 7,
                "image_key": "/images/image.jpg",
                "expiration_date": "2023-12-31",
            }
        },
        json_encoders={date: lambda v: v.isoformat()},
    )


class ProductUpdate(BaseUpdate):
    """
    Product model for the API request.
    """

    name: Optional[str] = Field(None, description="Product's name")
    short_description: Optional[str] = Field(None, description="Short description of the product")
    price: Optional[float] = Field(None, description="Product's price", gt=0)
    cost: Optional[float] = Field(None, description="Product's cost", gt=0)
    minimum_stock: Optional[int] = Field(
        None, description="Minimum stock level of the product", gt=0
    )
    expiration_date: Optional[date] = Field(
        None, description="Expiration date of the consumable product"
    )

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ejemplo de producto de papelería",
                "short_description": "Este es un producto de papelería de ejemplo.",
                "price": 9.99,
                "cost": 5.99,
                "minimum_stock": 7,
                "expiration_date": "2023-12-31",
                "updated_at": "2023-12-31T00:00:00Z",
            }
        },
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()},
    )


class CategoryCreate(BaseCreate):
    """
    Category model for the API request.
    """

    name: str = Field(..., description="Category's name")
    description: str = Field(..., description="Category's description")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "name": "Ejemplo de categoría",
                "description": "Descripción de la categoría de ejemplo.",
            }
        },
    )


class CategoryRead(BaseRead):
    """
    Category model for the API response.
    """

    id: int = Field(..., description="Category's unique identifier")
    name: str = Field(..., description="Category's name")
    description: str = Field(..., description="Category's description")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Ejemplo de categoría",
                "description": "Descripción de la categoría de ejemplo.",
            }
        },
    )


class CategoryUpdate(BaseUpdate):
    """
    Category model for the API request.
    """

    name: Optional[str] = Field(None, description="Category's name")
    description: Optional[str] = Field(None, description="Category's description")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "name": "Ejemplo de categoría",
                "description": "Descripción de la categoría de ejemplo.",
                "update_at": "2023-12-31T00:00:00Z",
            }
        },
    )
