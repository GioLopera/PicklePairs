from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.room import RoomCreate, RoomResponse, RoomCreatedResponse
from app.schemas.player import PlayerResponse
from app.services import room_service, player_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


def _get_open_room(room_code: str, db: Session):
    room = room_service.get_room(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already closed")
    return room


def _verify_creator(room, x_creator_token: str | None):
    if not x_creator_token or not room_service.verify_creator_token(room, x_creator_token):
        raise HTTPException(status_code=403, detail="Invalid or missing creator token")


@router.post("/", response_model=RoomCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_room(data: RoomCreate, db: Session = Depends(get_db)):
    room = room_service.create_room(db, data)
    return room


@router.get("/{room_code}", response_model=RoomResponse)
def get_room(room_code: str, db: Session = Depends(get_db)):
    return _get_open_room(room_code, db)


@router.delete("/{room_code}", status_code=status.HTTP_204_NO_CONTENT)
def close_room(
    room_code: str,
    x_creator_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    room = _get_open_room(room_code, db)
    _verify_creator(room, x_creator_token)
    room_service.close_room(db, room)
