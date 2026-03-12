from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# from core import SETTINGS
from .client import Client


class InvoiceItem(BaseModel):
    name: str
    quantity: int
    unit_price: float

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price

    model_config: ConfigDict = ConfigDict(str_to_lower=False)


class Invoice(BaseModel):
    number: int = Field(..., description="Invoice number")  # Id of order
    date: datetime = Field(..., description="Date of the invoice")
    client: "Client" = Field(..., description="Client associated with the invoice")
    items: list[InvoiceItem] = Field(
        default_factory=list, description="List of items in the invoice"
    )
    tax_rate: float = Field(0.0, description="Tax rate applied to the invoice")

    @property
    def total(self) -> float:
        return sum(item.total for item in self.items) + self.tax_amount

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def tax_amount(self) -> float:
        return self.subtotal * self.tax_rate

    model_config: ConfigDict = ConfigDict(str_to_lower=False)


class InvoiceRequest(BaseModel):
    order_id: int = Field(..., description="Order ID for which the invoice is generated")
    tax_rate: float = Field(0.0, description="Tax rate applied to the invoice")

    model_config: ConfigDict = ConfigDict(
        str_to_lower=True,
        str_strip_whitespace=True,
        json_schema_extra={"example": {"order_id": 1, "tax_rate": 0.15}},
    )
