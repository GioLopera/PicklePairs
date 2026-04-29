from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class PlayerJoin(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be blank")
        return v


class PlayerResponse(BaseModel):
    id: UUID
    name: str
    joined_at: datetime

    model_config = {"from_attributes": True}
