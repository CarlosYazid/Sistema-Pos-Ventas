from typing import Any, Dict, List, Optional

from fastapi_mail import MessageType
from pydantic import BaseModel, EmailStr

from .abc import AbstractCreate, AbstractUpdate, BaseCreate, BaseUpdate, UserCreate, UserUpdate
from .client import ClientCreate, ClientRead, ClientUpdate
from .employee import (
    EmployeeCreate,
    EmployeeProfileComplete,
    EmployeeRead,
    EmployeeUpdate,
)
from .order import OrderCreate, OrderRead, OrderUpdate
from .payment import PaymentCreate, PaymentRead, PaymentUpdate
from .product import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
    ProductCreate,
    ProductRead,
    ProductUpdate,
)
from .service import ServiceCreate, ServiceRead, ServiceUpdate

__all__ = [
    "AbstractCreate",
    "AbstractUpdate",
    "BaseCreate",
    "BaseUpdate",
    "UserCreate",
    "UserUpdate",
    "ClientCreate",
    "ClientRead",
    "ClientUpdate",
    "EmployeeCreate",
    "EmployeeRead",
    "EmployeeUpdate",
    "EmployeeLogin",
    "EmployeeProfileComplete",
    "PaymentCreate",
    "PaymentRead",
    "PaymentUpdate",
    "CategoryCreate",
    "CategoryRead",
    "CategoryUpdate",
    "ProductCreate",
    "ProductRead",
    "ProductUpdate",
    "ServiceCreate",
    "ServiceRead",
    "ServiceUpdate",
    "OrderCreate",
    "OrderRead",
    "OrderUpdate",
    "EmailSchema",
]


class EmailSchema(BaseModel):
    body: Optional[str]
    subject: str
    recipients: List[EmailStr]
    subtype: MessageType
    template_body: Optional[Dict[str, Any]]
