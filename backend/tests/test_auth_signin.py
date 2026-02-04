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

def test_signin_success(client: TestClient):
    """Test successful user signin."""
    # First create a user
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    # Then sign in
    response = client.post(
        "/auth/signin",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"

def test_signin_invalid_email(client: TestClient):
    """Test signin with non-existent email."""
    response = client.post(
        "/auth/signin",
        json={"email": "nonexistent@example.com", "password": "TestPass123"}
    )

    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_signin_invalid_password(client: TestClient):
    """Test signin with incorrect password."""
    # Create a user
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    # Try to sign in with wrong password
    response = client.post(
        "/auth/signin",
        json={"email": "test@example.com", "password": "WrongPass123"}
    )

    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_signin_case_insensitive_email(client: TestClient):
    """Test signin with different email case."""
    # Create user with lowercase email
    client.post(
        "/auth/signup",
        json={"email": "test@example.com", "password": "TestPass123"}
    )

    # Sign in with uppercase email
    response = client.post(
        "/auth/signin",
        json={"email": "TEST@EXAMPLE.COM", "password": "TestPass123"}
    )

    assert response.status_code == 200
