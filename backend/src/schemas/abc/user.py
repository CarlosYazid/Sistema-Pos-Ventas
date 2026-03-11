from typing import Optional

from pydantic import EmailStr, Field

from .base import BaseBase, BaseCreate, BaseRead, BaseUpdate


class UserBase(BaseBase):
    documentid: Optional[int] = Field(None, description="User's document ID", gt=0)
    phone: Optional[str] = Field(None, description="User's phone number")
    first_name: Optional[str] = Field(None, description="User's firstname")
    last_name: Optional[str] = Field(None, description="User's lastname")
    status: bool = Field(default=True, description="Is the user active?")


class UserCreate(UserBase, BaseCreate):
    email: EmailStr = Field(..., description="User's email address")


class UserUpdate(UserBase, BaseUpdate):
    email: Optional[EmailStr] = Field(None, description="User's email address")
    status: Optional[bool] = Field(None, description="Is the user active?")


class UserRead(UserBase, BaseRead):
    email: EmailStr = Field(..., description="User's email address")
    status: bool = Field(..., description="Is the user active?")
