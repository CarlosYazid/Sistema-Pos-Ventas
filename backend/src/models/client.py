from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship

from .abc import UserModel

if TYPE_CHECKING:
    from .order import Order
    from .payment import Payment


class Client(UserModel, table=True):
    orders: Optional[list["Order"]] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={"lazy": "selectin", "cascade": "all, delete-orphan"},
    )
    payments: Optional[list["Payment"]] = Relationship(
        back_populates="client",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
