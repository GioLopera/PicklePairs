from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.team import TeamResultResponse
from app.services import room_service, player_service, team_service
from app.websockets.room_ws import manager

router = APIRouter(prefix="/rooms", tags=["teams"])


def _verify_creator(room, x_creator_token: str | None):
    if not x_creator_token or not room_service.verify_creator_token(room, x_creator_token):
        raise HTTPException(status_code=403, detail="Invalid or missing creator token")


@router.post("/{room_code}/run", response_model=TeamResultResponse, status_code=status.HTTP_201_CREATED)
async def run_teams(
    room_code: str,
    x_creator_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    room = room_service.get_room(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already closed")

    _verify_creator(room, x_creator_token)

    players = player_service.list_players(db, room)

    try:
        result = team_service.generate_teams(db, room, players)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Broadcast result to all connected clients
    await manager.broadcast(room_code, {
        "type": "teams_generated",
        "result": result.model_dump(mode="json"),
    })

    return result


@router.get("/{room_code}/results/latest", response_model=TeamResultResponse | None)
def get_latest_result(room_code: str, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found or already closed")
    return team_service.get_latest_result(db, room)
