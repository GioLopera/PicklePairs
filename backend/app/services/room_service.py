import secrets
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.room import Room
from app.schemas.room import RoomCreate

DEFAULT_ROOM_NAME = "Pickleball Fun Room"
ROOM_CODE_MIN = 1000
ROOM_CODE_MAX = 9999


def _generate_room_code(db: Session) -> str:
    """Generate a unique 4-digit numeric room code (1000-9999)."""
    for _ in range(50):  # retry up to 50 times on collision
        code = str(secrets.randbelow(ROOM_CODE_MAX - ROOM_CODE_MIN + 1) + ROOM_CODE_MIN)
        if not db.query(Room).filter(Room.room_code == code).first():
            return code
    raise RuntimeError("Failed to generate a unique room code — pool may be exhausted")


def create_room(db: Session, data: RoomCreate) -> Room:
    room = Room(
        room_code=_generate_room_code(db),
        name=data.name.strip() if data.name and data.name.strip() else DEFAULT_ROOM_NAME,
        creator_token=secrets.token_hex(32),
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def get_room(db: Session, room_code: str) -> Room | None:
    return db.query(Room).filter(Room.room_code == room_code, Room.status == "open").first()


def close_room(db: Session, room: Room) -> Room:
    room.status = "closed"
    room.closed_at = datetime.utcnow()
    db.commit()
    db.refresh(room)
    return room


def verify_creator_token(room: Room, token: str) -> bool:
    return secrets.compare_digest(room.creator_token, token)
