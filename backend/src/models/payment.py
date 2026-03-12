from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Relationship

from .abc import BaseModel

if TYPE_CHECKING:
    from .client import Client


class PaymentMethod(str, Enum):
    """
    Enum for payment methods.
    """

    CASH = "Efectivo"
    BANK_TRANSFER = "Transferencia_bancaria"
    ON_CREDIT = "Crédito_en_tiempo"


class PaymentStatus(str, Enum):
    """
    Enum for payment statuses.
    """

    PENDING = "Pendiente"
    COMPLETED = "Completado"
    FAILED = "Fallido"
    REFUNDED = "Reembolsado"


class Payment(BaseModel, table=True):
    """
    Model for payments.
    """

    client_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("client.id", ondelete="CASCADE"),
            index=True,
            nullable=False,
        )
    )

    amount: float = Field(..., description="Amount paid")
    method: PaymentMethod = Field(..., description="Payment method used")
    status: PaymentStatus = Field(..., description="Current status of the payment")
    due_date: Optional[date] = Field(None, description="Due date for the credit payment")
    interest_rate: Optional[float] = Field(None, description="Interest rate applied to the credit")
    account_number: Optional[str] = Field(None, description="Account number for the bank transfer")

    client: "Client" = Relationship(
        back_populates="payments",
        sa_relationship_kwargs={"lazy": "selectin"},
    )
