import pytest
import sys
import os

# Make sure app is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.main import app


@pytest.fixture
def client():
    """Fresh test client + reset state before each test."""
    import app.main as main_module
    main_module.tasks = []
    main_module.next_id = 1
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Health & Home ──────────────────────────────────────────────────────────────

def test_home_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"running" in res.data


def test_health_check(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


# ── GET /tasks ─────────────────────────────────────────────────────────────────

def test_get_tasks_empty(client):
    res = client.get("/tasks")
    assert res.status_code == 200
    assert res.get_json()["tasks"] == []
    assert res.get_json()["count"] == 0


def test_get_tasks_after_create(client):
    client.post("/tasks", json={"title": "Buy milk"})
    client.post("/tasks", json={"title": "Walk dog"})
    res = client.get("/tasks")
    assert res.get_json()["count"] == 2


# ── POST /tasks ────────────────────────────────────────────────────────────────

def test_create_task_success(client):
    res = client.post("/tasks", json={"title": "Write tests"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["title"] == "Write tests"
    assert data["done"] is False
    assert data["id"] == 1


def test_create_task_missing_title(client):
    res = client.post("/tasks", json={"note": "oops"})
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_create_task_no_body(client):
    res = client.post("/tasks", content_type="application/json", data="")
    assert res.status_code == 400


def test_create_multiple_tasks_ids_increment(client):
    res1 = client.post("/tasks", json={"title": "First"})
    res2 = client.post("/tasks", json={"title": "Second"})
    assert res1.get_json()["id"] == 1
    assert res2.get_json()["id"] == 2


# ── PATCH /tasks/<id> ──────────────────────────────────────────────────────────

def test_update_task_done(client):
    client.post("/tasks", json={"title": "Fix bug"})
    res = client.patch("/tasks/1", json={"done": True})
    assert res.status_code == 200
    assert res.get_json()["done"] is True


def test_update_task_title(client):
    client.post("/tasks", json={"title": "Old title"})
    res = client.patch("/tasks/1", json={"title": "New title"})
    assert res.get_json()["title"] == "New title"


def test_update_task_not_found(client):
    res = client.patch("/tasks/999", json={"done": True})
    assert res.status_code == 404


# ── DELETE /tasks/<id> ────────────────────────────────────────────────────────

def test_delete_task_success(client):
    client.post("/tasks", json={"title": "To delete"})
    res = client.delete("/tasks/1")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Task 1 deleted"


def test_delete_task_removes_from_list(client):
    client.post("/tasks", json={"title": "Keep me"})
    client.post("/tasks", json={"title": "Delete me"})
    client.delete("/tasks/2")
    res = client.get("/tasks")
    assert res.get_json()["count"] == 1
    assert res.get_json()["tasks"][0]["title"] == "Keep me"


def test_delete_task_not_found(client):
    res = client.delete("/tasks/999")
    assert res.status_code == 404