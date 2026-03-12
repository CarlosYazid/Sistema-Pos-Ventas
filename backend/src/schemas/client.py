from datetime import datetime

from pydantic import ConfigDict

from .abc import UserCreate, UserRead, UserUpdate


class ClientCreate(UserCreate):
    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "documentid": 1234567890,
                "email": "doro@example.com",
                "phone": "555-555-5555",
                "first_name": "Dorotea",
                "last_name": "Hernandez",
            }
        },
    )


class ClientUpdate(UserUpdate):
    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "doro@example.com",
                "phone": "555-555-5555",
                "first_name": "Dorotea",
                "last_name": "Hernandez",
                "status": True,
                "updated_at": datetime.now(),
            }
        },
    )


class ClientRead(UserRead):
    model_config: ConfigDict = ConfigDict(
        str_strip_whitespace=True,
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
