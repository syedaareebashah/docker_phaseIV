"""Integration tests for complete task API workflow."""
import pytest
from fastapi.testclient import TestClient
import time


def test_complete_crud_workflow(client: TestClient, auth_headers: dict):
    """Test complete CRUD workflow: create → list → get → update → toggle → delete."""
    user_id = auth_headers["user_id"]

    # 1. Create task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Integration Test Task", "description": "Test description"},
        headers={"Authorization": auth_headers["token"]}
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]
    assert create_response.json()["completed"] is False

    # 2. Verify in list
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks) >= 1
    assert any(task["id"] == task_id for task in tasks)

    # 3. Get task
    get_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Integration Test Task"

    # 4. Update task
    update_response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={"title": "Updated Task Title"},
        headers={"Authorization": auth_headers["token"]}
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Task Title"

    # 5. Toggle completion
    toggle_response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        headers={"Authorization": auth_headers["token"]}
    )
    assert toggle_response.status_code == 200
    assert toggle_response.json()["completed"] is True

    # 6. Delete task
    delete_response = client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": auth_headers["token"]}
    )
    assert delete_response.status_code == 204

    # 7. Verify not in list
    final_list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )
    final_tasks = final_list_response.json()
    assert not any(task["id"] == task_id for task in final_tasks)


def test_user_isolation_across_all_operations(client: TestClient, auth_headers: dict):
    """Test user isolation: two users cannot access each other's tasks."""
    user1_id = auth_headers["user_id"]
    user1_token = auth_headers["token"]

    # Create second user
    signup_response = client.post(
        "/auth/signup",
        json={"email": "user2@example.com", "password": "Password123"}
    )
    user2_id = signup_response.json()["user"]["user_id"]
    user2_token = f"Bearer {signup_response.json()['token']}"

    # User 1 creates task
    user1_task_response = client.post(
        f"/api/{user1_id}/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": user1_token}
    )
    user1_task_id = user1_task_response.json()["id"]

    # User 2 creates task
    user2_task_response = client.post(
        f"/api/{user2_id}/tasks",
        json={"title": "User 2 Task"},
        headers={"Authorization": user2_token}
    )
    user2_task_id = user2_task_response.json()["id"]

    # User 1 cannot see user 2's task in list
    user1_list = client.get(
        f"/api/{user1_id}/tasks",
        headers={"Authorization": user1_token}
    ).json()
    assert not any(task["id"] == user2_task_id for task in user1_list)

    # User 2 cannot see user 1's task in list
    user2_list = client.get(
        f"/api/{user2_id}/tasks",
        headers={"Authorization": user2_token}
    ).json()
    assert not any(task["id"] == user1_task_id for task in user2_list)

    # User 1 cannot get user 2's task
    get_response = client.get(
        f"/api/{user1_id}/tasks/{user2_task_id}",
        headers={"Authorization": user1_token}
    )
    assert get_response.status_code == 404

    # User 1 cannot update user 2's task
    update_response = client.put(
        f"/api/{user1_id}/tasks/{user2_task_id}",
        json={"title": "Hacked"},
        headers={"Authorization": user1_token}
    )
    assert update_response.status_code == 404

    # User 1 cannot toggle user 2's task
    toggle_response = client.patch(
        f"/api/{user1_id}/tasks/{user2_task_id}/complete",
        headers={"Authorization": user1_token}
    )
    assert toggle_response.status_code == 404

    # User 1 cannot delete user 2's task
    delete_response = client.delete(
        f"/api/{user1_id}/tasks/{user2_task_id}",
        headers={"Authorization": user1_token}
    )
    assert delete_response.status_code == 404

    # Verify user 2's task still exists
    verify_response = client.get(
        f"/api/{user2_id}/tasks/{user2_task_id}",
        headers={"Authorization": user2_token}
    )
    assert verify_response.status_code == 200


def test_concurrent_task_creation(client: TestClient, auth_headers: dict):
    """Test concurrent task creation by same user succeeds."""
    user_id = auth_headers["user_id"]

    # Create multiple tasks rapidly
    task_ids = []
    for i in range(5):
        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": f"Concurrent Task {i}"},
            headers={"Authorization": auth_headers["token"]}
        )
        assert response.status_code == 201
        task_ids.append(response.json()["id"])

    # Verify all tasks exist
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )
    tasks = list_response.json()
    created_task_ids = [task["id"] for task in tasks]

    for task_id in task_ids:
        assert task_id in created_task_ids


def test_error_responses_consistent_format(client: TestClient, auth_headers: dict):
    """Test all error responses have consistent format with 'detail' field."""
    user_id = auth_headers["user_id"]

    # 400 Bad Request (validation error)
    response_400 = client.post(
        f"/api/{user_id}/tasks",
        json={"title": ""},
        headers={"Authorization": auth_headers["token"]}
    )
    assert response_400.status_code == 422
    assert "detail" in response_400.json()

    # 401 Unauthorized
    response_401 = client.get(f"/api/{user_id}/tasks")
    assert response_401.status_code == 401
    assert "detail" in response_401.json()

    # 403 Forbidden
    from uuid import uuid4
    different_user_id = str(uuid4())
    response_403 = client.get(
        f"/api/{different_user_id}/tasks",
        headers={"Authorization": auth_headers["token"]}
    )
    assert response_403.status_code == 403
    assert "detail" in response_403.json()

    # 404 Not Found
    non_existent_id = str(uuid4())
    response_404 = client.get(
        f"/api/{user_id}/tasks/{non_existent_id}",
        headers={"Authorization": auth_headers["token"]}
    )
    assert response_404.status_code == 404
    assert "detail" in response_404.json()


def test_authentication_integration(client: TestClient):
    """Test Feature 1 authentication integration."""
    # Valid token succeeds
    signup_response = client.post(
        "/auth/signup",
        json={"email": "authtest@example.com", "password": "Password123"}
    )
    assert signup_response.status_code == 201
    token = signup_response.json()["token"]
    user_id = signup_response.json()["user"]["user_id"]

    # Create task with valid token
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={"title": "Auth Test Task"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_response.status_code == 201

    # Invalid token fails
    invalid_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert invalid_response.status_code == 401

    # No token fails
    no_token_response = client.get(f"/api/{user_id}/tasks")
    assert no_token_response.status_code == 401
