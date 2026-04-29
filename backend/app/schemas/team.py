from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TeamPair(BaseModel):
    team_number: int
    players: list[str]


class WaitingPlayer(BaseModel):
    player: str


class TeamResultResponse(BaseModel):
    result_id: UUID
    run_number: int
    generated_at: datetime
    teams: list[TeamPair]
    waiting_player: WaitingPlayer | None = None
