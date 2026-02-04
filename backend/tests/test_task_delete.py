"""Tests for task deletion endpoint."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_delete_task_success(client: TestClient, auth_headers: dict):
    """Test deleting a task removes it from database."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Task to Delete"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Delete task
    response = client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 204
    assert response.content == b""


def test_delete_task_not_in_list(client: TestClient, auth_headers: dict):
    """Test deleted task no longer appears in list."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Task to Delete"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Delete task
    client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    # Verify not in list
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )
    tasks = list_response.json()
    task_ids = [task["id"] for task in tasks]
    assert task_id not in task_ids


def test_delete_task_subsequent_get_fails(client: TestClient, auth_headers: dict):
    """Test subsequent get request for deleted task returns 404."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Task to Delete"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Delete task
    client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    # Try to get deleted task
    get_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )
    assert get_response.status_code == 404


def test_delete_task_not_found(client: TestClient, auth_headers: dict):
    """Test deleting non-existent task returns 404."""
    user_id = auth_headers["user_id"]
    non_existent_id = str(uuid4())

    response = client.delete(
        f"/api/{user_id}/tasks/{non_existent_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404


def test_delete_task_other_user(client: TestClient, auth_headers: dict):
    """Test deleting other user's task returns 404."""
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

    # Try to delete user 2's task as user 1
    response = client.delete(
        f"/api/{user1_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404

    # Verify task still exists for user 2
    get_response = client.get(
        f"/api/{user2_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert get_response.status_code == 200


def test_delete_task_mismatched_user_id(client: TestClient, auth_headers: dict):
    """Test deleting with mismatched user_id returns 403."""
    different_user_id = str(uuid4())
    task_id = str(uuid4())

    response = client.delete(
        f"/api/{different_user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 403


def test_delete_task_without_authentication(client: TestClient, auth_headers: dict):
    """Test deleting without authentication returns 401."""
    user_id = auth_headers["user_id"]
    task_id = str(uuid4())

    response = client.delete(f"/api/{user_id}/tasks/{task_id}")

    assert response.status_code == 401
