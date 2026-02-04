# Research Findings: Authentication & User Isolation

**Feature ID:** 1-auth-user-isolation
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This document consolidates research findings for technical decisions made during the planning phase of the Authentication & User Isolation feature. Each decision includes rationale, alternatives considered, and implementation guidance.

---

## R1: Better Auth JWT Plugin Configuration

### Decision
Use Better Auth with JWT plugin for Next.js frontend authentication, configured to generate JWT tokens compatible with FastAPI backend verification.

### Rationale
- **Better Auth** is a modern authentication library designed for Next.js App Router
- **JWT Plugin** provides built-in JWT token generation with customizable payload
- **Compatibility** with backend JWT verification (HS256 algorithm)
- **Flexibility** allows custom token expiration and payload structure
- **Type Safety** with TypeScript support

### Alternatives Considered

**1. NextAuth.js**
- Pros: Mature, widely adopted, extensive provider support
- Cons: Primarily session-based, JWT support less flexible, heavier weight
- Verdict: Rejected - Better Auth provides more control over JWT structure

**2. Custom JWT Implementation**
- Pros: Full control, minimal dependencies
- Cons: Reinventing the wheel, security risks, maintenance burden
- Verdict: Rejected - Better Auth provides battle-tested implementation

**3. Auth0 / Clerk**
- Pros: Managed service, comprehensive features
- Cons: External dependency, cost, vendor lock-in
- Verdict: Rejected - Project requires self-hosted solution

### Implementation Guidance

**Installation:**
```bash
npm install better-auth
```

**Configuration (lib/auth.ts):**
```typescript
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
  database: {
    // Database connection for Better Auth's internal tables
    provider: "postgresql",
    url: process.env.DATABASE_URL
  },
  plugins: [
    jwt({
      // JWT configuration
      secret: process.env.BETTER_AUTH_SECRET!,
      expiresIn: "1h", // 1 hour expiration
      algorithm: "HS256",
      // Custom payload
      payload: (user) => ({
        user_id: user.id,
        email: user.email
      })
    })
  ],
  emailAndPassword: {
    enabled: true,
    // Password validation
    minPasswordLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: false
  }
})
```

**Token Storage:**
```typescript
// Store token in localStorage after successful authentication
localStorage.setItem('auth_token', token)

// Retrieve token for API calls
const token = localStorage.getItem('auth_token')

// Clear token on logout
localStorage.removeItem('auth_token')
```

### References
- Better Auth Documentation: https://www.better-auth.com/
- JWT Plugin: https://www.better-auth.com/docs/plugins/jwt

---

## R2: FastAPI JWT Middleware Implementation

### Decision
Use FastAPI dependency injection with `Depends()` for JWT verification rather than traditional middleware. Create a reusable dependency that verifies JWT and injects authenticated user into route handlers.

### Rationale
- **Dependency Injection** is FastAPI's recommended pattern for authentication
- **Reusability** - Single dependency can be used across all protected routes
- **Type Safety** - Provides typed user object to route handlers
- **Flexibility** - Easy to make routes optional or required authentication
- **Testability** - Dependencies can be easily mocked in tests

### Alternatives Considered

**1. Traditional Middleware**
- Pros: Intercepts all requests automatically
- Cons: Less flexible, harder to exclude specific routes, no type safety
- Verdict: Rejected - Dependency injection provides better developer experience

**2. Decorator Pattern**
- Pros: Clean syntax with @require_auth decorator
- Cons: Not idiomatic FastAPI, loses type safety benefits
- Verdict: Rejected - FastAPI dependencies are more powerful

**3. Manual Token Verification in Each Route**
- Pros: Maximum control
- Cons: Code duplication, error-prone, maintenance nightmare
- Verdict: Rejected - Violates DRY principle

### Implementation Guidance

**JWT Utilities (auth/jwt.py):**
```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status
import os

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
EXPIRATION_HOURS = 1

def create_access_token(user_id: str, email: str) -> str:
    """Generate JWT token with user information."""
    expire = datetime.utcnow() + timedelta(hours=EXPIRATION_HOURS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

**Authentication Dependency (auth/dependencies.py):**
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from .jwt import verify_token
from .database import get_session
from .models import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Verify JWT token and return authenticated user.

    Raises:
        HTTPException: 401 if token invalid/expired, 404 if user not found
    """
    # Verify token
    payload = verify_token(credentials.credentials)

    # Extract user_id
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Look up user
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
```

**Usage in Routes:**
```python
from fastapi import APIRouter, Depends
from .auth.dependencies import get_current_user
from .models import User

router = APIRouter()

@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    """Protected route - requires valid JWT."""
    return {"message": f"Hello {current_user.email}"}
```

### Library Choice: python-jose vs PyJWT

**Decision:** Use `python-jose[cryptography]`

**Rationale:**
- More comprehensive cryptographic support
- Better maintained for production use
- Includes additional security features
- FastAPI documentation examples use python-jose

**Installation:**
```bash
pip install "python-jose[cryptography]"
```

### References
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
- python-jose: https://python-jose.readthedocs.io/

---

## R3: Password Hashing Best Practices

### Decision
Use `passlib` with `bcrypt` scheme and 12 rounds (higher than minimum 10 for extra security).

### Rationale
- **passlib** is the industry-standard password hashing library for Python
- **bcrypt** is cryptographically secure and resistant to rainbow table attacks
- **12 rounds** provides strong security while maintaining acceptable performance
- **Automatic salt generation** prevents rainbow table attacks
- **Constant-time comparison** prevents timing attacks

### Alternatives Considered

**1. bcrypt library directly**
- Pros: Simpler, fewer dependencies
- Cons: Less flexible, no algorithm migration support
- Verdict: Rejected - passlib provides better long-term maintainability

**2. argon2**
- Pros: More modern, winner of Password Hashing Competition
- Cons: Less widely adopted, higher memory requirements
- Verdict: Considered for future upgrade, bcrypt sufficient for now

**3. PBKDF2**
- Pros: Built into Python standard library
- Cons: Less resistant to GPU attacks than bcrypt
- Verdict: Rejected - bcrypt is superior

### Implementation Guidance

**Installation:**
```bash
pip install "passlib[bcrypt]"
```

**Password Utilities (auth/password.py):**
```python
from passlib.context import CryptContext
import re

# Configure password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # 12 rounds for strong security
)

def hash_password(password: str) -> str:
    """Hash password using bcrypt with 12 rounds."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash using constant-time comparison.

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets complexity requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number

    Returns:
        tuple: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"

    return True, ""
```

**Usage:**
```python
# Hash password before storing
password_hash = hash_password(user_password)

# Verify password during signin
if not verify_password(provided_password, stored_hash):
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Validate password strength during signup
is_valid, error = validate_password_strength(password)
if not is_valid:
    raise HTTPException(status_code=400, detail=error)
```

### Security Considerations

**Timing Attack Prevention:**
- `passlib.verify()` uses constant-time comparison
- Always verify password even if user doesn't exist (same response time)

**Salt Management:**
- Salt automatically generated and stored with hash
- No need to manage salts separately

**Hash Upgrade Path:**
- passlib supports automatic hash upgrades
- Can migrate to stronger algorithms in future without breaking existing hashes

### References
- passlib Documentation: https://passlib.readthedocs.io/
- OWASP Password Storage: https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

## R4: Frontend HTTP Client with Token Injection

### Decision
Use Axios with request interceptors to automatically attach JWT token to all API requests.

### Rationale
- **Axios** provides clean interceptor API for request/response modification
- **Automatic Token Injection** - No need to manually add headers in each API call
- **Centralized Error Handling** - 401 errors handled in one place
- **TypeScript Support** - Full type safety for requests/responses
- **Widely Adopted** - Large community, extensive documentation

### Alternatives Considered

**1. Native fetch with wrapper**
- Pros: No dependencies, built into browser
- Cons: More boilerplate, less elegant interceptor pattern
- Verdict: Rejected - Axios provides better developer experience

**2. SWR / React Query**
- Pros: Built-in caching, revalidation, optimistic updates
- Cons: Overkill for simple authentication, adds complexity
- Verdict: Consider for future enhancement, not needed initially

**3. tRPC**
- Pros: End-to-end type safety, no API contracts needed
- Cons: Requires TypeScript on backend, major architectural change
- Verdict: Rejected - Project uses REST API

### Implementation Guidance

**Installation:**
```bash
npm install axios
```

**API Client Setup (lib/api-client.ts):**
```typescript
import axios, { AxiosInstance, AxiosError } from 'axios'
import { useRouter } from 'next/navigation'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor - attach JWT token
apiClient.interceptors.request.use(
  (config) => {
    // Get token from localStorage
    const token = localStorage.getItem('auth_token')

    // Attach token if exists
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle authentication errors
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error: AxiosError) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // Clear token
      localStorage.removeItem('auth_token')

      // Redirect to signin
      if (typeof window !== 'undefined') {
        window.location.href = '/signin'
      }
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      // Show error message (implement toast/notification)
      console.error('Access forbidden')
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

**Usage in Components:**
```typescript
import apiClient from '@/lib/api-client'

// Signup
const signup = async (email: string, password: string) => {
  const response = await apiClient.post('/auth/signup', { email, password })
  const { token, user } = response.data

  // Store token
  localStorage.setItem('auth_token', token)

  return user
}

// Protected API call (token automatically attached)
const getTodos = async () => {
  const response = await apiClient.get('/todos')
  return response.data
}
```

### References
- Axios Documentation: https://axios-http.com/
- Axios Interceptors: https://axios-http.com/docs/interceptors

---

## R5: User Isolation Enforcement Patterns

### Decision
Implement user isolation through a combination of:
1. FastAPI dependency that injects authenticated user
2. Route-level validation that user_id matches authenticated user
3. Database query filtering by authenticated user_id

### Rationale
- **Defense in Depth** - Multiple layers of protection
- **Explicit Validation** - Clear, auditable security checks
- **Type Safety** - Compiler catches missing checks
- **Testability** - Easy to verify isolation in tests

### Implementation Guidance

**Pattern 1: Route Parameter Validation**
```python
@router.get("/users/{user_id}/todos")
async def get_user_todos(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Get todos for specific user (must be authenticated user)."""

    # Enforce user isolation
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Query todos filtered by user_id
    todos = session.query(Todo).filter(Todo.user_id == user_id).all()
    return todos
```

**Pattern 2: Automatic Filtering**
```python
@router.get("/todos")
async def get_my_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get todos for authenticated user (no user_id in path)."""

    # Automatically filter by authenticated user
    todos = session.query(Todo).filter(
        Todo.user_id == current_user.user_id
    ).all()

    return todos
```

**Pattern 3: Resource Ownership Validation**
```python
@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete todo (must be owned by authenticated user)."""

    # Look up todo
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Verify ownership
    if todo.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden"
        )

    # Delete todo
    session.delete(todo)
    session.commit()

    return {"message": "Todo deleted"}
```

### Testing User Isolation

```python
def test_user_isolation():
    """Test that users cannot access other users' data."""

    # Create two users
    user1 = create_test_user("user1@example.com")
    user2 = create_test_user("user2@example.com")

    # User1 creates a todo
    token1 = get_auth_token(user1)
    response = client.post(
        "/todos",
        json={"title": "User1's todo"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    todo_id = response.json()["id"]

    # User2 attempts to access User1's todo
    token2 = get_auth_token(user2)
    response = client.get(
        f"/todos/{todo_id}",
        headers={"Authorization": f"Bearer {token2}"}
    )

    # Should return 403 Forbidden
    assert response.status_code == 403
```

### References
- FastAPI Dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- OWASP Access Control: https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

---

## Summary

All research topics have been resolved with concrete implementation guidance. Key decisions:

1. **Better Auth + JWT Plugin** for frontend authentication
2. **FastAPI Dependencies** for backend JWT verification
3. **passlib + bcrypt (12 rounds)** for password hashing
4. **Axios with interceptors** for automatic token injection
5. **Multi-layer user isolation** with explicit validation

These decisions align with project constitution principles and provide a secure, maintainable authentication system.

---

**End of Research Findings**
