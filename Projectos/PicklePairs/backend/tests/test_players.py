import pytest
from fastapi.testclient import TestClient


def _create_room(client: TestClient) -> dict:
    return client.post("/rooms/", json={}).json()


def test_join_room(client: TestClient):
    room = _create_room(client)
    res = client.post(f"/rooms/{room['room_code']}/players", json={"name": "Alice"})
    assert res.status_code == 201
    assert res.json()["name"] == "Alice"


def test_join_room_duplicate_name(client: TestClient):
    room = _create_room(client)
    client.post(f"/rooms/{room['room_code']}/players", json={"name": "Alice"})
    res = client.post(f"/rooms/{room['room_code']}/players", json={"name": "Alice"})
    assert res.status_code == 409


def test_join_room_blank_name(client: TestClient):
    room = _create_room(client)
    res = client.post(f"/rooms/{room['room_code']}/players", json={"name": "   "})
    assert res.status_code == 422


def test_list_players(client: TestClient):
    room = _create_room(client)
    for name in ["Alice", "Bob", "Carol"]:
        client.post(f"/rooms/{room['room_code']}/players", json={"name": name})

    res = client.get(f"/rooms/{room['room_code']}/players")
    assert res.status_code == 200
    names = [p["name"] for p in res.json()]
    assert sorted(names) == ["Alice", "Bob", "Carol"]


def test_join_nonexistent_room(client: TestClient):
    res = client.post("/rooms/xxxxxx/players", json={"name": "Alice"})
    assert res.status_code == 404
