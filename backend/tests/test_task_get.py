"""Tests for get single task endpoint."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_get_task_success(client: TestClient, auth_headers: dict):
    """Test getting a task returns task details."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task", "description": "Test description"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Get task
    response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task"
    assert data["description"] == "Test description"
    assert data["user_id"] == user_id


def test_get_task_not_found(client: TestClient, auth_headers: dict):
    """Test getting non-existent task returns 404."""
    user_id = auth_headers["user_id"]
    non_existent_id = str(uuid4())

    response = client.get(
        f"/api/{user_id}/tasks/{non_existent_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404


def test_get_task_other_user(client: TestClient, auth_headers: dict):
    """Test getting other user's task returns 404 (not 403)."""
    user1_id = auth_headers["user_id"]

    # Create second user
    signup_response = client.post(
        "/auth/signup",
        json={"email": "user2@example.com", "password": "Password123"}
    )
    user2_token = signup_response.json()["token"]
    user2_id = signup_response.json()["user"]["user_id"]

    # Create task for user 2
    create_response = client.post(
        f"/api/{user2_id}/tasks",
        json={"title": "User 2 Task"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    task_id = create_response.json()["id"]

    # Try to get user 2's task as user 1
    response = client.get(
        f"/api/{user1_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    # Should return 404, not 403, to avoid revealing task existence
    assert response.status_code == 404


def test_get_task_mismatched_user_id(client: TestClient, auth_headers: dict):
    """Test getting task with mismatched user_id returns 403."""
    different_user_id = str(uuid4())
    task_id = str(uuid4())

    response = client.get(
        f"/api/{different_user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 403


def test_get_task_without_authentication(client: TestClient, auth_headers: dict):
    """Test getting task without authentication returns 401."""
    user_id = auth_headers["user_id"]
    task_id = str(uuid4())

    response = client.get(f"/api/{user_id}/tasks/{task_id}")

    assert response.status_code == 401
