from typing import Any, Optional

from pydantic import BaseModel


class TaskResult(BaseModel):
    status: str
    result: Optional[dict[str, Any]]

class InvoiceCreate(BaseModel):
    order_id: int
    tax_rate: Optional[float]