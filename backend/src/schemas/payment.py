from datetime import date
from typing import Optional

from pydantic import ConfigDict, Field

from models import PaymentMethod, PaymentStatus

from .abc import BaseCreate, BaseRead, BaseUpdate


class PaymentCreate(BaseCreate):
    client_id: int = Field(..., description="Client associated with the payment", gt=0)
    amount: float = Field(..., description="Amount paid", gt=0)
    method: PaymentMethod = Field(default=PaymentMethod.CASH, description="Payment method used")
    status: PaymentStatus = Field(
        default=PaymentStatus.PENDING, description="Current status of the payment"
    )
    due_date: Optional[date] = Field(None, description="Due date for the credit payment")
    interest_rate: Optional[float] = Field(
        None, description="Interest rate applied to the credit", gt=0
    )
    account_number: Optional[str] = Field(
        None, description="Account number for the bank transfer", gt=0
    )

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "client_id": 1,
                "amount": 1000.00,
                "method": "Crédito_en_tiempo",
                "status": "Pendiente",
                "due_date": "2023-01-01",
                "interest_rate": 0.05,
                "account_number": "1234567890",
            }
        },
    )


class PaymentUpdate(BaseUpdate):
    amount: Optional[float] = Field(None, description="Amount paid", gt=0)
    method: Optional[PaymentMethod] = Field(None, description="Payment method used")
    status: Optional[PaymentStatus] = Field(None, description="Current status of the payment")
    due_date: Optional[date] = Field(None, description="Due date for the credit payment")
    interest_rate: Optional[float] = Field(
        None, description="Interest rate applied to the credit", gt=0
    )
    account_number: Optional[str] = Field(
        None, description="Account number for the bank transfer", gt=0
    )

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "amount": 1000.00,
                "method": "Crédito_en_tiempo",
                "status": "Pendiente",
                "due_date": "2023-01-01",
                "interest_rate": 0.05,
                "account_number": "1234567890",
                "updated_at": "2023-01-01T00:00:00Z",
            }
        },
    )


class PaymentRead(BaseRead):
    client_id: int = Field(..., description="Client associated with the payment")
    amount: float = Field(..., description="Amount paid")
    method: PaymentMethod = Field(..., description="Payment method used")
    status: PaymentStatus = Field(..., description="Current status of the payment")
    due_date: Optional[date] = Field(None, description="Due date for the credit payment")
    interest_rate: Optional[float] = Field(None, description="Interest rate applied to the credit")
    account_number: Optional[str] = Field(None, description="Account number for the bank transfer")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "client_id": 1,
                "amount": 1000.00,
                "method": "Crédito_en_tiempo",
                "status": "Pendiente",
                "due_date": "2023-01-01",
                "interest_rate": 0.05,
                "account_number": "1234567890",
            }
        },
    )
