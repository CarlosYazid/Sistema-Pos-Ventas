from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import text

class BaseModel(SQLModel):
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"server_default": text("now()")}
        )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"server_default": text("now()")}
        )

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"
