"""Tests for task update endpoint."""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4


def test_update_task_all_fields(client: TestClient, auth_headers: dict):
    """Test updating all fields updates task correctly."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title", "description": "Original description"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Update task
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated description",
            "completed": True
        },
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["completed"] is True


def test_update_task_title_only(client: TestClient, auth_headers: dict):
    """Test updating only title leaves other fields unchanged."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title", "description": "Original description"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]
    original_description = create_response.json()["description"]

    # Update only title
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": "New Title"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == original_description
    assert data["completed"] is False


def test_update_task_description_only(client: TestClient, auth_headers: dict):
    """Test updating only description leaves other fields unchanged."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title", "description": "Original description"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]
    original_title = create_response.json()["title"]

    # Update only description
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"description": "New description"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == original_title
    assert data["description"] == "New description"
    assert data["completed"] is False


def test_update_task_completed_only(client: TestClient, auth_headers: dict):
    """Test updating only completed status leaves other fields unchanged."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title", "description": "Original description"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]
    original_title = create_response.json()["title"]
    original_description = create_response.json()["description"]

    # Update only completed status
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"completed": True},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == original_title
    assert data["description"] == original_description
    assert data["completed"] is True


def test_update_task_empty_title(client: TestClient, auth_headers: dict):
    """Test updating with empty title returns 422."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Try to update with empty title
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": ""},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 422


def test_update_task_title_too_long(client: TestClient, auth_headers: dict):
    """Test updating with title > 255 chars returns 422."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]

    # Try to update with long title
    long_title = "x" * 256
    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": long_title},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 422


def test_update_task_not_found(client: TestClient, auth_headers: dict):
    """Test updating non-existent task returns 404."""
    user_id = auth_headers["user_id"]
    non_existent_id = str(uuid4())

    response = client.put(
        f"/api/{user_id}/tasks/{non_existent_id}",
        json={"title": "New Title"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404


def test_update_task_other_user(client: TestClient, auth_headers: dict):
    """Test updating other user's task returns 404."""
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

    # Try to update user 2's task as user 1
    response = client.put(
        f"/api/{user1_id}/tasks/{task_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 404


def test_update_task_mismatched_user_id(client: TestClient, auth_headers: dict):
    """Test updating task with mismatched user_id returns 403."""
    different_user_id = str(uuid4())
    task_id = str(uuid4())

    response = client.put(
        f"/api/{different_user_id}/tasks/{task_id}",
        json={"title": "New Title"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 403


def test_update_task_without_authentication(client: TestClient, auth_headers: dict):
    """Test updating task without authentication returns 401."""
    user_id = auth_headers["user_id"]
    task_id = str(uuid4())

    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": "New Title"}
    )

    assert response.status_code == 401


def test_update_task_timestamp_changes(client: TestClient, auth_headers: dict):
    """Test updated_at timestamp changes after update."""
    user_id = auth_headers["user_id"]

    # Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Original Title"},
        headers={"Authorization": auth_headers["token"]}
    )
    task_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    # Wait a moment and update
    import time
    time.sleep(0.1)

    response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": "Updated Title"},
        headers={"Authorization": auth_headers["token"]}
    )

    assert response.status_code == 200
    new_updated_at = response.json()["updated_at"]
    assert new_updated_at != original_updated_at
