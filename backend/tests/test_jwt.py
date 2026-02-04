import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from app.auth.jwt import create_access_token, verify_token
from fastapi import HTTPException

def test_create_access_token():
    """Test JWT token creation."""
    user_id = uuid4()
    email = "test@example.com"

    token = create_access_token(user_id, email)

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0

def test_verify_token_valid():
    """Test JWT token verification with valid token."""
    user_id = uuid4()
    email = "test@example.com"

    token = create_access_token(user_id, email)
    payload = verify_token(token)

    # Verify payload contains expected fields
    assert payload["user_id"] == str(user_id)
    assert payload["email"] == email
    assert "exp" in payload
    assert "iat" in payload

def test_verify_token_invalid():
    """Test JWT token verification with invalid token."""
    with pytest.raises(HTTPException) as exc_info:
        verify_token("invalid.token.here")

    assert exc_info.value.status_code == 401
    assert "Invalid authentication credentials" in exc_info.value.detail

def test_verify_token_malformed():
    """Test JWT token verification with malformed token."""
    with pytest.raises(HTTPException) as exc_info:
        verify_token("not-a-jwt-token")

    assert exc_info.value.status_code == 401
