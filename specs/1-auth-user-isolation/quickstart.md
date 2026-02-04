# Quickstart Guide: Authentication & User Isolation

**Feature ID:** 1-auth-user-isolation
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This guide provides step-by-step instructions for setting up and using the Authentication & User Isolation system in the Todo Full-Stack Web Application.

**What You'll Learn:**
- How to configure environment variables
- How to protect API endpoints with authentication
- How to access authenticated user information
- How to create protected frontend routes
- How to troubleshoot common issues

---

## Prerequisites

**Backend:**
- Python 3.10+
- FastAPI installed
- SQLModel installed
- python-jose[cryptography] installed
- passlib[bcrypt] installed
- Neon PostgreSQL database

**Frontend:**
- Node.js 18+
- Next.js 16+ (App Router)
- Better Auth installed
- Axios installed

---

## Setup Instructions

### Step 1: Generate Shared Secret

The authentication system requires a shared secret (BETTER_AUTH_SECRET) that must be identical in both frontend and backend.

**Generate a secure random secret:**

```bash
# Using OpenSSL (recommended)
openssl rand -base64 32

# Using Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Using Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('base64'))"
```

**Example output:**
```
dGhpc2lzYXNlY3VyZXJhbmRvbXNlY3JldGtleQ==
```

⚠️ **Important:** Keep this secret secure and never commit it to version control!

### Step 2: Configure Backend Environment

Create `.env` file in backend root:

```bash
# Backend .env
BETTER_AUTH_SECRET=dGhpc2lzYXNlY3VyZXJhbmRvbXNlY3JldGtleQ==
JWT_EXPIRATION_HOURS=1
DATABASE_URL=postgresql://user:password@host:5432/database
```

**Verify configuration:**
```python
import os
print(f"Secret configured: {bool(os.getenv('BETTER_AUTH_SECRET'))}")
print(f"Secret length: {len(os.getenv('BETTER_AUTH_SECRET', ''))}")
```

### Step 3: Configure Frontend Environment

Create `.env.local` file in frontend root:

```bash
# Frontend .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=dGhpc2lzYXNlY3VyZXJhbmRvbXNlY3JldGtleQ==
```

⚠️ **Critical:** BETTER_AUTH_SECRET must match exactly between frontend and backend!

### Step 4: Run Database Migrations

Apply the user table migration:

```bash
# Backend directory
alembic upgrade head
```

**Verify migration:**
```sql
-- Connect to database and verify users table exists
\dt users
```

### Step 5: Start Services

**Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm run dev
```

**Verify services:**
- Backend: http://localhost:8000/docs (OpenAPI documentation)
- Frontend: http://localhost:3000

---

## Usage Guide

### Protecting API Endpoints

**Step 1: Import authentication dependency**

```python
from auth.dependencies import get_current_user
from models import User
from fastapi import Depends
```

**Step 2: Add dependency to route**

```python
@router.get("/protected-endpoint")
async def protected_route(
    current_user: User = Depends(get_current_user)
):
    """
    This endpoint requires valid JWT token.
    current_user contains authenticated user information.
    """
    return {
        "message": f"Hello {current_user.email}",
        "user_id": str(current_user.user_id)
    }
```

**That's it!** The endpoint now:
- ✅ Requires valid JWT token
- ✅ Returns 401 if token missing/invalid/expired
- ✅ Provides authenticated user object
- ✅ Enforces user isolation

### Accessing Authenticated User

The `current_user` object provides:

```python
current_user.user_id    # UUID - Unique user identifier
current_user.email      # str - User's email address
current_user.created_at # datetime - Account creation time
```

**Example: Filter data by authenticated user**

```python
@router.get("/todos")
async def get_my_todos(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get todos for authenticated user only."""

    # Automatically filter by authenticated user
    todos = session.query(Todo).filter(
        Todo.user_id == current_user.user_id
    ).all()

    return todos
```

### Enforcing User Isolation

**Pattern 1: Validate route parameter matches authenticated user**

```python
@router.get("/users/{user_id}/profile")
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """User can only access their own profile."""

    # Enforce user isolation
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )

    # Proceed with operation
    return {"user_id": user_id, "email": current_user.email}
```

**Pattern 2: Validate resource ownership**

```python
@router.delete("/todos/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """User can only delete their own todos."""

    # Look up todo
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Verify ownership
    if todo.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Delete todo
    session.delete(todo)
    session.commit()

    return {"message": "Todo deleted"}
```

### Creating Protected Frontend Routes

**Step 1: Create ProtectedRoute component**

```typescript
// components/ProtectedRoute.tsx
'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function ProtectedRoute({
  children
}: {
  children: React.ReactNode
}) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/signin')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}
```

**Step 2: Wrap protected pages**

```typescript
// app/dashboard/page.tsx
import ProtectedRoute from '@/components/ProtectedRoute'

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div>
        <h1>Dashboard</h1>
        <p>This page requires authentication</p>
      </div>
    </ProtectedRoute>
  )
}
```

### Making Authenticated API Calls

**The API client automatically attaches JWT token to all requests:**

```typescript
import apiClient from '@/lib/api-client'

// No need to manually add Authorization header!
const getTodos = async () => {
  const response = await apiClient.get('/todos')
  return response.data
}

const createTodo = async (title: string) => {
  const response = await apiClient.post('/todos', { title })
  return response.data
}
```

**Token is automatically:**
- ✅ Retrieved from localStorage
- ✅ Attached to Authorization header
- ✅ Sent with every request
- ✅ Handled on 401 errors (redirect to signin)

---

## Testing

### Test Authentication Flow

**1. Test Signup:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

**Expected response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "test@example.com",
    "created_at": "2026-02-03T12:00:00Z"
  }
}
```

**2. Test Signin:**
```bash
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'
```

**3. Test Protected Endpoint:**
```bash
# Save token from signup/signin response
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Call protected endpoint
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected response:**
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "test@example.com",
  "created_at": "2026-02-03T12:00:00Z"
}
```

**4. Test Without Token (should fail):**
```bash
curl -X GET http://localhost:8000/auth/me
```

**Expected response:**
```json
{
  "detail": "Not authenticated"
}
```

### Run Integration Tests

**Backend:**
```bash
cd backend
pytest tests/test_auth.py -v
```

**Frontend:**
```bash
cd frontend
npm test -- auth.test.tsx
```

---

## Troubleshooting

### Issue: "Invalid authentication credentials"

**Symptoms:**
- All API requests return 401
- Token appears valid but is rejected

**Possible Causes:**
1. BETTER_AUTH_SECRET mismatch between frontend and backend
2. Token expired (1 hour expiration)
3. Token corrupted during storage/transmission

**Solutions:**

**1. Verify secrets match:**
```bash
# Backend
echo $BETTER_AUTH_SECRET

# Frontend
echo $BETTER_AUTH_SECRET
```

**2. Check token expiration:**
```typescript
// Decode token to check expiration (client-side)
const token = localStorage.getItem('auth_token')
const payload = JSON.parse(atob(token.split('.')[1]))
const expiresAt = new Date(payload.exp * 1000)
console.log('Token expires at:', expiresAt)
console.log('Is expired:', expiresAt < new Date())
```

**3. Clear token and re-authenticate:**
```typescript
localStorage.removeItem('auth_token')
// Navigate to /signin
```

### Issue: "Access forbidden" (403)

**Symptoms:**
- Token is valid but access denied
- User can authenticate but cannot access resources

**Possible Causes:**
1. Attempting to access another user's resources
2. user_id mismatch in route parameters
3. Resource ownership validation failing

**Solutions:**

**1. Verify user_id matches:**
```python
# Add logging to debug
print(f"Authenticated user: {current_user.user_id}")
print(f"Requested user: {user_id}")
print(f"Match: {current_user.user_id == user_id}")
```

**2. Check resource ownership:**
```python
# Verify resource belongs to authenticated user
print(f"Resource owner: {resource.user_id}")
print(f"Authenticated user: {current_user.user_id}")
```

### Issue: Token not attached to requests

**Symptoms:**
- Frontend makes API calls but receives 401
- Token exists in localStorage but not sent

**Possible Causes:**
1. Not using centralized API client
2. Axios interceptor not configured
3. Token key mismatch

**Solutions:**

**1. Verify using API client:**
```typescript
// ❌ Wrong - bypasses interceptor
fetch('/api/todos')

// ✅ Correct - uses interceptor
import apiClient from '@/lib/api-client'
apiClient.get('/todos')
```

**2. Verify token in localStorage:**
```typescript
const token = localStorage.getItem('auth_token')
console.log('Token exists:', !!token)
console.log('Token length:', token?.length)
```

**3. Check request headers:**
```typescript
// In browser DevTools Network tab
// Verify Authorization header is present:
// Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Issue: Password validation failing

**Symptoms:**
- Signup fails with "Password requirements not met"
- Password appears to meet requirements

**Possible Causes:**
1. Password doesn't meet complexity rules
2. Validation logic mismatch between frontend and backend

**Solutions:**

**1. Verify password requirements:**
- Minimum 8 characters ✓
- At least one uppercase letter (A-Z) ✓
- At least one lowercase letter (a-z) ✓
- At least one number (0-9) ✓
- No special characters required ✓

**2. Test password validation:**
```python
from auth.password import validate_password_strength

password = "TestPass123"
is_valid, error = validate_password_strength(password)
print(f"Valid: {is_valid}, Error: {error}")
```

### Issue: Database connection errors

**Symptoms:**
- "Could not connect to database"
- Authentication endpoints fail

**Solutions:**

**1. Verify DATABASE_URL:**
```bash
echo $DATABASE_URL
# Should be: postgresql://user:password@host:5432/database
```

**2. Test database connection:**
```python
from sqlmodel import create_engine

engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    result = conn.execute("SELECT 1")
    print("Database connected:", result.fetchone())
```

**3. Verify users table exists:**
```sql
SELECT * FROM users LIMIT 1;
```

---

## Security Checklist

Before deploying to production, verify:

- [ ] BETTER_AUTH_SECRET is strong (32+ characters, random)
- [ ] BETTER_AUTH_SECRET matches between frontend and backend
- [ ] .env files are not committed to version control
- [ ] HTTPS is enforced for all authentication endpoints
- [ ] All API endpoints require authentication (except signup/signin)
- [ ] User isolation is enforced on all protected resources
- [ ] Password hashing uses bcrypt with 10+ rounds
- [ ] Generic error messages prevent user enumeration
- [ ] Token expiration is set to 1 hour
- [ ] CORS is properly configured for frontend domain

---

## Quick Reference

### Environment Variables

| Variable | Location | Required | Example |
|----------|----------|----------|---------|
| BETTER_AUTH_SECRET | Backend + Frontend | Yes | `dGhpc2lzYXNlY3VyZXJhbmRvbXNlY3JldGtleQ==` |
| JWT_EXPIRATION_HOURS | Backend | Yes | `1` |
| DATABASE_URL | Backend | Yes | `postgresql://user:pass@host:5432/db` |
| NEXT_PUBLIC_API_URL | Frontend | Yes | `http://localhost:8000` |

### API Endpoints

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| /auth/signup | POST | No | Create new user account |
| /auth/signin | POST | No | Authenticate existing user |
| /auth/me | GET | Yes | Get current user info |

### Common Commands

```bash
# Generate secret
openssl rand -base64 32

# Run migrations
alembic upgrade head

# Start backend
uvicorn main:app --reload

# Start frontend
npm run dev

# Run tests
pytest tests/test_auth.py
npm test
```

---

## Next Steps

Now that authentication is set up, you can:

1. **Create protected API endpoints** for your application features
2. **Build protected frontend pages** that require authentication
3. **Implement user-specific features** using authenticated user context
4. **Add authorization logic** for role-based access control (future enhancement)

For more information, see:
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/auth-api.yaml)
- [Research Findings](./research.md)

---

**End of Quickstart Guide**
