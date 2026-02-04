import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session

# Create in-memory SQLite database for testing
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

def test_get_current_user_success(client: TestClient):
    """Test /auth/me endpoint with valid token."""
    # Create and sign in user
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )
    token = response.json()["token"]

    # Get current user info
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "user_id" in data

def test_get_current_user_no_token(client: TestClient):
    """Test /auth/me endpoint without token."""
    response = client.get("/auth/me")

    assert response.status_code == 403  # HTTPBearer returns 403 for missing token

def test_get_current_user_invalid_token(client: TestClient):
    """Test /auth/me endpoint with invalid token."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )

    assert response.status_code == 401
