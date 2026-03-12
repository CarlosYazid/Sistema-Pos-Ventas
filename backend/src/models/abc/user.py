from typing import Optional

from pydantic import EmailStr
from sqlmodel import Field

from .base import BaseModel


class UserModel(BaseModel):
    documentid: Optional[int] = Field(
        default=None, description="User's document ID", index=True, unique=True
    )
    email: EmailStr = Field(..., description="User's email address", index=True, unique=True)
    phone: Optional[str] = Field(default=None, description="User's phone number")
    first_name: Optional[str] = Field(default=None, description="User's firstname")
    last_name: Optional[str] = Field(default=None, description="User's lastname")
    status: bool = Field(default=True, description="Is the user active?")

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
