"""Tests for task list endpoint."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_list_tasks_empty(client: TestClient, auth_headers: dict):
    """Test listing tasks returns empty array for user with no tasks."""
    user_id = auth_headers["user_id"]
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_returns_user_tasks(client: TestClient, auth_headers: dict):
    """Test listing tasks returns user's tasks in correct order."""
    user_id = auth_headers["user_id"]

    # Create multiple tasks
    task_titles = ["First Task", "Second Task", "Third Task"]
    for title in task_titles:
        client.post(
            f"/api/{user_id}/tasks",
            json={"title": title},
            headers={"Authorization": auth_headers["token"]}
        )

    # List tasks
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3

    # Verify newest first (reverse order)
    assert tasks[0]["title"] == "Third Task"
    assert tasks[1]["title"] == "Second Task"
    assert tasks[2]["title"] == "First Task"


def test_list_tasks_user_isolation(client: TestClient, auth_headers: dict):
    """Test listing tasks does not include other users' tasks."""
    user1_id = auth_headers["user_id"]

    # Create task for user 1
    client.post(
        f"/api/{user1_id}/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": auth_headers["token"]}
    )

    # Create second user
    signup_response = client.post(
        "/auth/signup",
        json={"email": "user2@example.com", "password": "Password123"}
    )
    user2_token = signup_response.json()["token"]
    user2_id = signup_response.json()["user"]["user_id"]

    # Create task for user 2
    client.post(
        f"/api/{user2_id}/tasks",
        json={"title": "User 2 Task"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )

    # List tasks for user 1
    response = client.get(
        f"/api/{user1_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "User 1 Task"
    assert tasks[0]["user_id"] == user1_id


def test_list_tasks_mismatched_user_id(client: TestClient, auth_headers: dict):
    """Test listing tasks with mismatched user_id returns 403."""
    different_user_id = str(uuid4())
    response = client.get(
        f"/api/{different_user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 403


def test_list_tasks_without_authentication(client: TestClient, auth_headers: dict):
    """Test listing tasks without authentication returns 401."""
    user_id = auth_headers["user_id"]
    response = client.get(f"/api/{user_id}/tasks")

    assert response.status_code == 401
