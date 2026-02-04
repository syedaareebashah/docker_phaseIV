---
name: auth-skill
description: Implement secure authentication with signup, signin, password hashing, JWT tokens, and Better Auth integration. Use for user authentication flows.
---

# Auth Skill – Authentication & Authorization

## Instructions

1. **User Signup**
   - Validate email format and uniqueness
   - Enforce password strength requirements (min 8 chars, complexity)
   - Hash password using bcrypt or argon2
   - Store user in database with hashed password
   - Return success response (no auto-login)

2. **User Signin**
   - Validate credentials against database
   - Verify password hash using bcrypt.compare()
   - Generate JWT token with user claims (id, email)
   - Set token expiration (e.g., 24 hours)
   - Return token to client

3. **JWT Token Management**
   - Sign tokens with secure secret from environment variables
   - Include user payload: `{ user_id, email, iat, exp }`
   - Verify token signature on protected routes
   - Decode user identity from valid tokens
   - Handle expired or invalid tokens gracefully

4. **Better Auth Integration**
   - Configure Better Auth in Next.js app
   - Set up JWT token issuance on login
   - Store tokens securely (httpOnly cookies preferred)
   - Implement auth context/provider for client state
   - Handle token refresh logic

5. **API Authentication**
   - Extract token from Authorization: Bearer <token> header
   - Create middleware to verify JWT on protected routes
   - Decode user_id from validated token
   - Pass authenticated user to route handlers
   - Return 401 for missing/invalid tokens

## Best Practices

- **Never store plaintext passwords** - always hash before database storage
- **Use environment variables** for JWT secret and Better Auth config
- **Implement HTTPS** in production for secure token transmission
- **Set token expiration** to balance security and user experience
- **Rate limit auth endpoints** to prevent brute force attacks
- **Log authentication events** for security monitoring
- **Validate all inputs** before processing
- **Use strong secrets** - minimum 32 characters, randomly generated
- **Separate concerns** - auth logic in dedicated middleware/utils

## Example Implementation

### Password Hashing (Python/FastAPI)
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed = pwd_context.hash(plain_password)

# Verify password
is_valid = pwd_context.verify(plain_password, hashed_password)
```

### JWT Token Generation (Python)
```python
from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

def create_token(user_id: str, email: str):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
```

### JWT Verification Middleware (FastAPI)
```python
from fastapi import Header, HTTPException
from jose import jwt, JWTError

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Better Auth Setup (Next.js)
```typescript
// lib/auth.ts
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  database: {
    // Neon PostgreSQL connection
  },
  jwt: {
    enabled: true,
    expiresIn: "24h"
  }
});

// app/api/auth/[...auth]/route.ts
export { GET, POST } from "@/lib/auth";
```

### Client-Side Auth (Next.js)
```typescript
// Store token
localStorage.setItem("token", jwtToken);

// Add to API requests
const response = await fetch("/api/tasks", {
  headers: {
    "Authorization": `Bearer ${token}`
  }
});
```

## Security Checklist

- [ ] Passwords hashed with bcrypt/argon2
- [ ] JWT secret stored in environment variable
- [ ] Token expiration set (not indefinite)
- [ ] HTTPS enabled in production
- [ ] Authorization header properly formatted
- [ ] Token signature verified on every protected request
- [ ] User ID from token matches request parameters
- [ ] Rate limiting on signup/signin endpoints
- [ ] Input validation on all auth fields
- [ ] Error messages don't leak security info
- [ ] Authentication logs maintained
- [ ] No sensitive data in JWT payload

## Common Errors & Solutions

**Error**: "Invalid token"
- Check token format: `Bearer <token>`
- Verify JWT secret matches between encode/decode
- Ensure token hasn't expired

**Error**: "Password hash verification failed"
- Confirm using same hashing algorithm (bcrypt)
- Check password stored as hash, not plaintext

**Error**: "CORS error on auth endpoint"
- Configure CORS to allow frontend origin
- Include credentials in fetch requests

**Error**: "User data leaking between accounts"
- Always filter queries by `user_id` from token
- Never trust user_id from request body/params