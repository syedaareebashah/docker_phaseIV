import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models.user import User

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

def test_signup_success(client: TestClient):
    """Test successful user signup."""
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert "user_id" in data["user"]

def test_signup_duplicate_email(client: TestClient):
    """Test signup with duplicate email."""
    # First signup
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    # Second signup with same email
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    assert response.status_code == 409
    assert "Email already exists" in response.json()["detail"]

def test_signup_weak_password(client: TestClient):
    """Test signup with weak password."""
    response = client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "weak"}
    )

    # Accept either 400 (validation error) or 422 (unprocessable entity) as both indicate rejection
    # Pydantic validation happens first, returning 422 with validation details
    assert response.status_code in [400, 422]
    # Check for weak password indicators in response
    response_text = str(response.json()) if response.status_code == 400 else str(response.text)
    assert "8 characters" in response_text or "Password" in response_text

def test_signup_invalid_email(client: TestClient):
    """Test signup with invalid email format."""
    response = client.post(
        "/auth/signup",
        json={"email": "not-an-email", "password": "TestPass123"}
    )

    assert response.status_code == 422  # Pydantic validation error
