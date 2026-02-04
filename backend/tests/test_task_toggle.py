"""Tests for task completion toggle endpoint."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_toggle_completion_false_to_true(client: TestClient, auth_headers: dict):
    """Test toggling completion from false to true."""
    user_id = auth_headers["user_id"]

    # Create task (defaults to completed=false)
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    # Toggle completion
    response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_toggle_completion_true_to_false(client: TestClient, auth_headers: dict):
    """Test toggling completion from true to false."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Set to completed
    client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"completed": True},
        headers={"Authorization": auth_headers["token"]}
    )

    # Toggle completion (should go back to false)
    response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    assert response.json()["completed"] is False


def test_toggle_completion_not_found(client: TestClient, auth_headers: dict):
    """Test toggling non-existent task returns 404."""
    user_id = auth_headers["user_id"]
    non_existent_id = str(uuid4())

    response = client.patch(
        f"/api/{user_id}/tasks/{non_existent_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404


def test_toggle_completion_other_user(client: TestClient, auth_headers: dict):
    """Test toggling other user's task returns 404."""
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

    # Try to toggle user 2's task as user 1
    response = client.patch(
        f"/api/{user1_id}/tasks/{task_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404


def test_toggle_completion_mismatched_user_id(client: TestClient, auth_headers: dict):
    """Test toggling with mismatched user_id returns 403."""
    different_user_id = str(uuid4())
    task_id = str(uuid4())

    response = client.patch(
        f"/api/{different_user_id}/tasks/{task_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 403


def test_toggle_completion_without_authentication(client: TestClient, auth_headers: dict):
    """Test toggling without authentication returns 401."""
    user_id = auth_headers["user_id"]
    task_id = str(uuid4())

    response = client.patch(f"/api/{user_id}/tasks/{task_id}/complete")

    assert response.status_code == 401


def test_toggle_completion_timestamp_changes(client: TestClient, auth_headers: dict):
    """Test updated_at timestamp changes after toggle."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    # Wait a moment and toggle
    import time
    time.sleep(0.1)

    response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    new_updated_at = response.json()["updated_at"]
    assert new_updated_at != original_updated_at
