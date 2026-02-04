import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

def test_user_isolation_own_profile(client: TestClient):
    """Test user can access their own profile."""
    # Create and sign in user
    response = client.post(
        "/auth/signup",
        json={"email": "user1@example.com", "password": "TestPass123"}
    )
    token = response.json()["token"]
    user_id = response.json()["user"]["user_id"]

    # Access own profile
    response = client.get(
        f"/api/{user_id}/profile",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "user1@example.com"

def test_user_isolation_other_user_profile(client: TestClient):
    """Test user cannot access another user's profile."""
    # Create user 1
    response1 = client.post(
        "/auth/signup",
        json={"email": "user1@example.com", "password": "TestPass123"}
    )
    token1 = response1.json()["token"]

    # Create user 2
    response2 = client.post(
        "/auth/signup",
        json={"email": "user2@example.com", "password": "TestPass123"}
    )
    user2_id = response2.json()["user"]["user_id"]

    # User 1 attempts to access User 2's profile
    response = client.get(
        f"/api/{user2_id}/profile",
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response.status_code == 403
    assert "Access forbidden" in response.json()["detail"]
