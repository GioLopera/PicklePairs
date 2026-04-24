from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.player import Player
from app.models.room import Room
from app.schemas.player import PlayerJoin


def join_room(db: Session, room: Room, data: PlayerJoin) -> Player:
    """Add a player to a room. Raises ValueError if name is already taken."""
    player = Player(room_id=room.id, name=data.name)
    db.add(player)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError(f"The name '{data.name}' is already taken in this room")
    db.refresh(player)
    return player


def list_players(db: Session, room: Room) -> list[Player]:
    return (
        db.query(Player)
        .filter(Player.room_id == room.id)
        .order_by(Player.joined_at)
        .all()
    )


def count_players(db: Session, room: Room) -> int:
    return db.query(Player).filter(Player.room_id == room.id).count()
