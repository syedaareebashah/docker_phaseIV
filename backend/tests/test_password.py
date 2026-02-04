import pytest
from app.auth.password import hash_password, verify_password, validate_password_strength

def test_hash_password():
    """Test password hashing produces bcrypt hash."""
    password = "TestPassword123"
    hashed = hash_password(password)

    # Bcrypt hashes start with $2b$
    assert hashed.startswith("$2b$")
    # Hash should be different from original password
    assert hashed != password

def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "TestPassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "TestPassword123"
    wrong_password = "WrongPassword123"
    hashed = hash_password(password)

    assert verify_password(wrong_password, hashed) is False

def test_validate_password_strength_valid():
    """Test password strength validation with valid password."""
    is_valid, error = validate_password_strength("ValidPass123")
    assert is_valid is True
    assert error == ""

def test_validate_password_strength_too_short():
    """Test password strength validation with short password."""
    is_valid, error = validate_password_strength("Short1")
    assert is_valid is False
    assert "8 characters" in error

def test_validate_password_strength_no_uppercase():
    """Test password strength validation without uppercase."""
    is_valid, error = validate_password_strength("lowercase123")
    assert is_valid is False
    assert "uppercase" in error

def test_validate_password_strength_no_lowercase():
    """Test password strength validation without lowercase."""
    is_valid, error = validate_password_strength("UPPERCASE123")
    assert is_valid is False
    assert "lowercase" in error

def test_validate_password_strength_no_number():
    """Test password strength validation without number."""
    is_valid, error = validate_password_strength("NoNumbers")
    assert is_valid is False
    assert "number" in error
