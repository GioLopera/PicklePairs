from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RoomCreate(BaseModel):
    name: str | None = None


class RoomResponse(BaseModel):
    room_code: str
    name: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RoomCreatedResponse(RoomResponse):
    # creator_token is only returned at creation time, never again
    creator_token: str
