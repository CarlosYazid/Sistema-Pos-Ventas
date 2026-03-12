from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from .abc import UserModel

if TYPE_CHECKING:
    from .order import Order


class Employee(UserModel, table=True):
    user_id: str = Field(index=True, unique=True, description="SuperTokens user id")
    birth_date: Optional[date] = Field(None, description="Employee's birth date")
    profile_completed: bool = Field(default=False, description="Has completed onboarding profile")

    orders: Optional[list["Order"]] = Relationship(
        back_populates="employee", sa_relationship_kwargs={"lazy": "selectin"}
    )
