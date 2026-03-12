from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .abc import UserCreate, UserRead, UserUpdate


class EmployeeCreate(UserCreate):
    user_id: str = Field(None, description="SuperTokens user id")
    birth_date: Optional[date] = Field(None, description="Employee's birth date")
    profile_completed: bool = Field(default=False, description="Has completed onboarding profile")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "documentid": 123456789,
                "email": "doro@example.com",
                "phone": "555-555-5555",
                "birth_date": "1990-01-01",
                "first_name": "Dorotea",
                "last_name": "Hernandez",
                "password": "92f728fh0fah98fh",
            }
        },
        json_encoders={date: lambda v: v.isoformat()},
    )


class EmployeeUpdate(UserUpdate):
    birth_date: Optional[date] = Field(None, description="Employee's birth date")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "doro@example.com",
                "phone": "555-555-5555",
                "first_name": "Dorotea",
                "last_name": "Hernandez",
                "status": True,
                "password": "92fh2hf9haf9f",
                "updated_at": "2023-01-02T00:00:00Z",
            }
        },
        json_encoders={date: lambda v: v.isoformat()},
    )


class EmployeeProfileComplete(BaseModel):
    user_id: str = Field(..., description="SuperTokens user id")
    email: EmailStr = Field(..., description="Email from Employee")
    documentid: int = Field(..., description="User's document ID", gt=0)
    phone: Optional[str] = Field(None, description="User's phone number")
    first_name: str = Field(..., description="User's firstname")
    last_name: str = Field(..., description="User's lastname")
    birth_date: date = Field(..., description="Employee's birth date")

    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "documentid": 123456789,
                "phone": "555-555-5555",
                "first_name": "Dorotea",
                "last_name": "Hernandez",
                "birth_date": "1990-01-01",
            }
        },
        json_encoders={date: lambda v: v.isoformat()},
    )


class EmployeeRead(UserRead):
    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        use_enum_values=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "documentid": 1234567890,
                "email": "doro@example.com",
                "phone": "555-555-5555",
                "first_name": "Dorotea",
                "last_name": "Hernandez",
                "status": True,
            }
        },
    )
