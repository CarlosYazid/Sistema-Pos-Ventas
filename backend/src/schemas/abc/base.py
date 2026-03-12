from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseBase(BaseModel):
    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_encoders={datetime: lambda v: v.isoformat(), date: lambda v: v.isoformat()},
    )


class BaseCreate(BaseBase):
    pass


class BaseUpdate(BaseBase):
    id: Optional[int] = Field(None, description="ID", gt=0)

    update_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the entity was last updated"
    )


class BaseRead(BaseModel):
    id: Optional[int] = Field(None, description="ID", gt=0)
