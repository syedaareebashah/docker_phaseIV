# Data Model: Authentication & User Isolation

**Feature ID:** 1-auth-user-isolation
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This document defines the data entities, relationships, and validation rules for the Authentication & User Isolation feature. The data model supports stateless JWT-based authentication with strict user isolation.

---

## Entities

### User

**Description:** Represents an authenticated user account in the system.

**Table Name:** `users`

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| user_id | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique identifier for the user |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for authentication) |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password (never plaintext) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last update timestamp |

**Indexes:**
- PRIMARY KEY on user_id
- UNIQUE INDEX on email (for fast lookup and duplicate prevention)

**Validation Rules:**

**Email:**
- Must be valid email format (RFC 5322 compliant)
- Must be unique across all users
- Case-insensitive comparison for uniqueness
- Maximum length: 255 characters

**Password (Pre-Hash):**
- Minimum length: 8 characters
- Must contain at least one uppercase letter (A-Z)
- Must contain at least one lowercase letter (a-z)
- Must contain at least one number (0-9)
- No special characters required
- Maximum length: 128 characters (before hashing)

**Password Hash:**
- Generated using bcrypt with minimum 10 rounds
- Never exposed in API responses
- Never logged or included in error messages

**Timestamps:**
- created_at: Set automatically on record creation, immutable
- updated_at: Set automatically on record creation, updated on any modification

**Relationships:**
- One user can have many tasks (defined in future task feature)
- User is the owner of all their tasks (enforced via user_id foreign key)

**Security Constraints:**
- password_hash field must never be included in API responses
- All queries must be filtered by authenticated user_id (user isolation)
- Email uniqueness prevents account enumeration via signup

---

## Logical Entities

### JWT Token

**Description:** Cryptographically signed token containing authenticated user information. Not stored in database; exists only in transit and client storage.

**Structure:**

**Header:**
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1738598400,
  "iat": 1738594800
}
```

**Signature:**
- Algorithm: HS256 (HMAC with SHA-256)
- Secret: BETTER_AUTH_SECRET (from environment variable)
- Format: HMACSHA256(base64UrlEncode(header) + "." + base64UrlEncode(payload), secret)

**Payload Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user_id | UUID (string) | Authenticated user's unique identifier |
| email | String | Authenticated user's email address |
| exp | Integer (Unix timestamp) | Token expiration time (issued_at + 1 hour) |
| iat | Integer (Unix timestamp) | Token issued-at time |

**Validation Rules:**
- Signature must be valid (verified using BETTER_AUTH_SECRET)
- exp must be in the future (not expired)
- user_id must be valid UUID format
- email must be valid email format

**Lifecycle:**
- Created: On successful signup or signin
- Stored: In client localStorage
- Transmitted: In Authorization header (Bearer <token>)
- Verified: On every API request by backend middleware
- Expires: After 1 hour (3600 seconds)
- Destroyed: On logout (removed from localStorage)

**Security Properties:**
- Stateless: No server-side storage required
- Tamper-proof: Any modification invalidates signature
- Time-limited: Expires after 1 hour
- Self-contained: Contains all necessary authentication information

---

## State Transitions

### User Account Lifecycle

```
[No Account]
    |
    | POST /auth/signup (valid email + password)
    v
[Account Created]
    |
    | (automatic)
    v
[Active Account]
    |
    | POST /auth/signin (valid credentials)
    v
[Authenticated Session]
    |
    | (1 hour passes OR logout)
    v
[Session Expired] --> POST /auth/signin --> [Authenticated Session]
```

**State Descriptions:**

1. **No Account:** User does not exist in system
2. **Account Created:** User record exists in database with hashed password
3. **Active Account:** User can authenticate but is not currently authenticated
4. **Authenticated Session:** User has valid JWT token, can access protected resources
5. **Session Expired:** JWT token expired, user must re-authenticate

**State Transition Rules:**
- Signup creates account and immediately issues token (skip Active Account state)
- Signin requires valid credentials (email + password match)
- Token expiration is automatic after 1 hour
- Logout is client-side only (token removed from localStorage)
- No server-side session state maintained

---

## Data Integrity Constraints

### Database Level

**Uniqueness:**
- Email addresses must be unique (enforced by UNIQUE constraint)
- user_id is primary key (automatically unique)

**Referential Integrity:**
- Future task records will reference users.user_id as foreign key
- ON DELETE CASCADE: Deleting user deletes all their tasks (future feature)

**Data Type Constraints:**
- user_id: Must be valid UUID v4
- email: Must be valid VARCHAR(255)
- password_hash: Must be valid VARCHAR(255)
- Timestamps: Must be valid TIMESTAMP values

### Application Level

**Password Security:**
- Plaintext passwords never stored in database
- Password hashing performed before database insert
- Password verification uses constant-time comparison
- Failed authentication uses generic error message

**User Isolation:**
- All data queries filtered by authenticated user_id
- Cross-user access attempts return 403 Forbidden
- No user can access another user's data

**Token Security:**
- Token signature verified on every request
- Expired tokens rejected with 401 Unauthorized
- Invalid tokens rejected with 401 Unauthorized
- Token payload user_id must match requested resource owner

---

## Database Schema (SQL)

```sql
-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create users table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for fast lookup
CREATE UNIQUE INDEX idx_users_email ON users(LOWER(email));

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## SQLModel Definition (Python)

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    """User account model for authentication."""

    __tablename__ = "users"

    user_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    email: str = Field(
        max_length=255,
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: str = Field(
        max_length=255,
        nullable=False
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-03T12:00:00Z",
                "updated_at": "2026-02-03T12:00:00Z"
            }
        }

class UserPublic(SQLModel):
    """Public user model (excludes password_hash)."""

    user_id: UUID
    email: str
    created_at: datetime

class UserCreate(SQLModel):
    """User creation model (signup request)."""

    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

class UserLogin(SQLModel):
    """User login model (signin request)."""

    email: str
    password: str
```

---

## Data Access Patterns

### Create User (Signup)
```python
# Validate password strength
validate_password_strength(password)

# Hash password
password_hash = hash_password(password)

# Create user
user = User(
    email=email.lower(),
    password_hash=password_hash
)

# Insert into database
session.add(user)
session.commit()
session.refresh(user)

# Generate JWT
token = create_access_token(user.user_id, user.email)

return {"token": token, "user": UserPublic.from_orm(user)}
```

### Authenticate User (Signin)
```python
# Look up user by email (case-insensitive)
user = session.query(User).filter(
    func.lower(User.email) == email.lower()
).first()

# Verify password (constant-time comparison)
if not user or not verify_password(password, user.password_hash):
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Generate JWT
token = create_access_token(user.user_id, user.email)

return {"token": token, "user": UserPublic.from_orm(user)}
```

### Get Authenticated User
```python
# Extract user_id from verified JWT
user_id = get_user_id_from_token(token)

# Look up user
user = session.query(User).filter(User.user_id == user_id).first()

if not user:
    raise HTTPException(status_code=401, detail="User not found")

return UserPublic.from_orm(user)
```

### Enforce User Isolation
```python
# Get authenticated user_id from JWT
authenticated_user_id = get_current_user_id()

# Verify requested resource belongs to authenticated user
if resource.user_id != authenticated_user_id:
    raise HTTPException(status_code=403, detail="Access forbidden")

# Proceed with operation
```

---

## Migration Strategy

### Initial Migration (Alembic)

**File:** `alembic/versions/001_create_users_table.py`

```python
"""Create users table

Revision ID: 001
Revises:
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create email index (case-insensitive)
    op.create_index(
        'idx_users_email',
        'users',
        [sa.text('LOWER(email)')],
        unique=True
    )

    # Create updated_at trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER update_users_updated_at
            BEFORE UPDATE ON users
            FOR EACH ROW
            EXECUTE FUNCTION update_updated_at_column();
    """)

def downgrade():
    op.drop_table('users')
    op.execute('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE')
```

---

## Testing Data

### Test Users

**Valid Test User:**
```json
{
  "email": "test@example.com",
  "password": "TestPass123"
}
```

**Expected Hash (bcrypt, 10 rounds):**
```
$2b$10$... (actual hash will vary due to salt)
```

**Test Scenarios:**
1. Create user with valid data → Success
2. Create user with duplicate email → 409 Conflict
3. Create user with invalid email → 400 Bad Request
4. Create user with weak password → 400 Bad Request
5. Authenticate with valid credentials → Success
6. Authenticate with invalid password → 401 Unauthorized
7. Authenticate with non-existent email → 401 Unauthorized

---

**End of Data Model**
