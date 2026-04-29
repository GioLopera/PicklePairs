from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.player import PlayerJoin, PlayerResponse
from app.services import room_service, player_service
from app.websockets.room_ws import manager

router = APIRouter(prefix="/rooms", tags=["players"])


@router.post("/{room_code}/players", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
async def join_room(room_code: str, data: PlayerJoin, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already closed")

    try:
        player = player_service.join_room(db, room, data)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Broadcast to all connected clients in this room
    await manager.broadcast(room_code, {
        "type": "player_joined",
        "player": {"id": str(player.id), "name": player.name},
    })

    return player


@router.get("/{room_code}/players", response_model=list[PlayerResponse])
def list_players(room_code: str, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already closed")
    return player_service.list_players(db, room)
