import pytest
from fastapi.testclient import TestClient


def test_create_room_default_name(client: TestClient):
    res = client.post("/rooms/", json={})
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Pickleball Fun Room"
    assert len(data["room_code"]) == 6
    assert "creator_token" in data
    assert data["status"] == "open"


def test_create_room_custom_name(client: TestClient):
    res = client.post("/rooms/", json={"name": "Tuesday Morning Group"})
    assert res.status_code == 201
    assert res.json()["name"] == "Tuesday Morning Group"


def test_create_room_blank_name_uses_default(client: TestClient):
    res = client.post("/rooms/", json={"name": "   "})
    assert res.status_code == 201
    assert res.json()["name"] == "Pickleball Fun Room"


def test_get_room(client: TestClient):
    created = client.post("/rooms/", json={}).json()
    res = client.get(f"/rooms/{created['room_code']}")
    assert res.status_code == 200
    assert res.json()["room_code"] == created["room_code"]


def test_get_nonexistent_room(client: TestClient):
    res = client.get("/rooms/xxxxxx")
    assert res.status_code == 404


def test_close_room(client: TestClient):
    created = client.post("/rooms/", json={}).json()
    res = client.delete(
        f"/rooms/{created['room_code']}",
        headers={"x-creator-token": created["creator_token"]},
    )
    assert res.status_code == 204

    # Room should no longer be findable
    assert client.get(f"/rooms/{created['room_code']}").status_code == 404


def test_close_room_wrong_token(client: TestClient):
    created = client.post("/rooms/", json={}).json()
    res = client.delete(
        f"/rooms/{created['room_code']}",
        headers={"x-creator-token": "wrong-token"},
    )
    assert res.status_code == 403
