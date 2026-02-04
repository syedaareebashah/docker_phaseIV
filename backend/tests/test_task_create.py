"""Tests for task creation endpoint."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_create_task_success(client: TestClient, auth_headers: dict):
    """Test creating a task with valid data returns 201 and task object."""
    user_id = auth_headers["user_id"]
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task", "description": "Test description"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert data["completed"] is False
    assert data["user_id"] == user_id
    assert "created_at" in data
    assert "updated_at" in data


def test_create_task_without_description(client: TestClient, auth_headers: dict):
    """Test creating a task without description succeeds."""
    user_id = auth_headers["user_id"]
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Task without description"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Task without description"
    assert data["description"] is None


def test_create_task_empty_title(client: TestClient, auth_headers: dict):
    """Test creating a task with empty title returns 400."""
    user_id = auth_headers["user_id"]
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "", "description": "Test"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 422  # Pydantic validation error


def test_create_task_title_too_long(client: TestClient, auth_headers: dict):
    """Test creating a task with title > 255 chars returns 422."""
    user_id = auth_headers["user_id"]
    long_title = "x" * 256
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": long_title, "description": "Test"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 422


def test_create_task_description_too_long(client: TestClient, auth_headers: dict):
    """Test creating a task with description > 1000 chars returns 422."""
    user_id = auth_headers["user_id"]
    long_description = "x" * 1001
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test", "description": long_description},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 422


def test_create_task_mismatched_user_id(client: TestClient, auth_headers: dict):
    """Test creating a task with mismatched user_id returns 403."""
    different_user_id = str(uuid4())
    response = client.post(
        f"/api/{different_user_id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()


def test_create_task_without_authentication(client: TestClient, auth_headers: dict):
    """Test creating a task without authentication returns 401."""
    user_id = auth_headers["user_id"]
    response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task"}
    )

    assert response.status_code == 401


def test_create_task_persists_to_database(client: TestClient, auth_headers: dict):
    """Test created task persists and can be retrieved."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Persistent Task"},
        headers={"Authorization": auth_headers["token"]}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # Retrieve task
    get_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Persistent Task"
