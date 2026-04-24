import random

from sqlalchemy.orm import Session

from app.models.player import Player
from app.models.room import Room
from app.models.team import TeamResult, TeamAssignment
from app.schemas.team import TeamResultResponse, TeamPair, WaitingPlayer

MIN_PLAYERS = 3


def _consecutive_pair_shuffle(players: list[Player]) -> tuple[list[tuple[Player, Player]], Player | None]:
    """
    Randomly shuffle players and form consecutive pairs.
    If the count is odd, the last player is returned as the waiting player.

    Returns:
        pairs: list of (player_a, player_b) tuples
        waiting: the leftover Player, or None if count is even
    """
    shuffled = random.sample(players, len(players))
    pairs = []

    for i in range(0, len(shuffled) - 1, 2):
        pairs.append((shuffled[i], shuffled[i + 1]))

    waiting = shuffled[-1] if len(shuffled) % 2 != 0 else None
    return pairs, waiting


def generate_teams(db: Session, room: Room, players: list[Player]) -> TeamResultResponse:
    if len(players) < MIN_PLAYERS:
        raise ValueError(f"At least {MIN_PLAYERS} players are required to generate teams")

    # Determine the next run number for this room
    last_result = (
        db.query(TeamResult)
        .filter(TeamResult.room_id == room.id)
        .order_by(TeamResult.run_number.desc())
        .first()
    )
    run_number = (last_result.run_number + 1) if last_result else 1

    # Run the algorithm
    pairs, waiting_player = _consecutive_pair_shuffle(players)

    # Persist the result
    result = TeamResult(room_id=room.id, run_number=run_number)
    db.add(result)
    db.flush()  # get result.id before adding assignments

    assignments = []
    for team_number, (player_a, player_b) in enumerate(pairs, start=1):
        assignments.append(TeamAssignment(
            result_id=result.id,
            player_id=player_a.id,
            team_number=team_number,
            status="playing",
        ))
        assignments.append(TeamAssignment(
            result_id=result.id,
            player_id=player_b.id,
            team_number=team_number,
            status="playing",
        ))

    if waiting_player:
        # Give the waiting player a team_number beyond the last team
        waiting_team_number = len(pairs) + 1
        assignments.append(TeamAssignment(
            result_id=result.id,
            player_id=waiting_player.id,
            team_number=waiting_team_number,
            status="waiting",
        ))

    db.add_all(assignments)
    db.commit()
    db.refresh(result)

    # Build the response
    teams = [
        TeamPair(
            team_number=team_number,
            players=[player_a.name, player_b.name],
        )
        for team_number, (player_a, player_b) in enumerate(pairs, start=1)
    ]

    return TeamResultResponse(
        result_id=result.id,
        run_number=run_number,
        generated_at=result.generated_at,
        teams=teams,
        waiting_player=WaitingPlayer(player=waiting_player.name) if waiting_player else None,
    )


def get_latest_result(db: Session, room: Room) -> TeamResultResponse | None:
    result = (
        db.query(TeamResult)
        .filter(TeamResult.room_id == room.id)
        .order_by(TeamResult.run_number.desc())
        .first()
    )
    if not result:
        return None

    teams: list[TeamPair] = []
    waiting_player: WaitingPlayer | None = None

    # Group assignments by team_number
    playing = [a for a in result.assignments if a.status == "playing"]
    waiting = [a for a in result.assignments if a.status == "waiting"]

    team_map: dict[int, list[str]] = {}
    for assignment in playing:
        team_map.setdefault(assignment.team_number, []).append(assignment.player.name)

    for team_number in sorted(team_map):
        teams.append(TeamPair(team_number=team_number, players=team_map[team_number]))

    if waiting:
        waiting_player = WaitingPlayer(player=waiting[0].player.name)

    return TeamResultResponse(
        result_id=result.id,
        run_number=result.run_number,
        generated_at=result.generated_at,
        teams=teams,
        waiting_player=waiting_player,
    )
