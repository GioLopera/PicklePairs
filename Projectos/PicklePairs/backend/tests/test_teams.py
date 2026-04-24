import pytest
from fastapi.testclient import TestClient


def _create_room(client: TestClient) -> dict:
    return client.post("/rooms/", json={}).json()


def _add_players(client: TestClient, room_code: str, names: list[str]):
    for name in names:
        client.post(f"/rooms/{room_code}/players", json={"name": name})


def _run_teams(client: TestClient, room: dict) -> dict:
    res = client.post(
        f"/rooms/{room['room_code']}/run",
        headers={"x-creator-token": room["creator_token"]},
    )
    return res


class TestTeamGeneration:
    def test_even_players_no_waiting(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob", "Carol", "Dave"])
        res = _run_teams(client, room)
        assert res.status_code == 201
        data = res.json()
        assert len(data["teams"]) == 2
        assert data["waiting_player"] is None
        for team in data["teams"]:
            assert len(team["players"]) == 2

    def test_odd_players_has_waiting(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob", "Carol"])
        res = _run_teams(client, room)
        assert res.status_code == 201
        data = res.json()
        assert len(data["teams"]) == 1
        assert data["waiting_player"] is not None
        assert data["waiting_player"]["player"] in ["Alice", "Bob", "Carol"]

    def test_five_players(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob", "Carol", "Dave", "Eve"])
        res = _run_teams(client, room)
        assert res.status_code == 201
        data = res.json()
        assert len(data["teams"]) == 2
        assert data["waiting_player"] is not None

    def test_all_players_accounted_for(self, client: TestClient):
        """Every player should appear exactly once across teams + waiting."""
        players = ["Alice", "Bob", "Carol", "Dave", "Eve"]
        room = _create_room(client)
        _add_players(client, room["room_code"], players)
        data = _run_teams(client, room).json()

        assigned = [p for team in data["teams"] for p in team["players"]]
        if data["waiting_player"]:
            assigned.append(data["waiting_player"]["player"])

        assert sorted(assigned) == sorted(players)

    def test_minimum_players_not_met(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob"])
        res = _run_teams(client, room)
        assert res.status_code == 422

    def test_run_requires_creator_token(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob", "Carol"])
        res = client.post(f"/rooms/{room['room_code']}/run")
        assert res.status_code == 403

    def test_rerun_increments_run_number(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob", "Carol", "Dave"])
        first = _run_teams(client, room).json()
        second = _run_teams(client, room).json()
        assert second["run_number"] == first["run_number"] + 1

    def test_get_latest_result(self, client: TestClient):
        room = _create_room(client)
        _add_players(client, room["room_code"], ["Alice", "Bob", "Carol", "Dave"])
        _run_teams(client, room)
        _run_teams(client, room)  # run twice
        res = client.get(f"/rooms/{room['room_code']}/results/latest")
        assert res.status_code == 200
        assert res.json()["run_number"] == 2

    def test_no_result_yet(self, client: TestClient):
        room = _create_room(client)
        res = client.get(f"/rooms/{room['room_code']}/results/latest")
        assert res.status_code == 200
        assert res.json() is None
