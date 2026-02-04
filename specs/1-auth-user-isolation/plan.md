# Implementation Plan: Authentication & User Isolation

**Feature ID:** 1-auth-user-isolation
**Version:** 1.0.0
**Status:** Draft
**Created:** 2026-02-03
**Last Updated:** 2026-02-03

---

## Executive Summary

This plan outlines the implementation strategy for secure, token-based authentication and user isolation in the Todo Full-Stack Web Application. The implementation follows a security-first approach where backend protection is established before frontend integration, ensuring no API endpoint is ever exposed without authentication.

**Key Objectives:**
- Implement stateless JWT-based authentication
- Enforce user isolation at API and database layers
- Ensure all API endpoints require valid authentication
- Prevent cross-user data access
- Maintain complete frontend/backend decoupling

**Implementation Approach:**
- Backend-first security layer (FastAPI JWT middleware)
- Frontend authentication integration (Next.js + Better Auth)
- Comprehensive validation and testing
- Zero manual coding (Claude Code + Spec-Kit Plus only)

---

## Technical Context

### Technology Stack

**Frontend:**
- Framework: Next.js 16+ (App Router)
- Authentication Library: Better Auth with JWT plugin
- Token Storage: localStorage
- HTTP Client: Axios or fetch with interceptors
- State Management: React Context API (for auth state)

**Backend:**
- Framework: FastAPI
- JWT Library: PyJWT or python-jose
- Password Hashing: bcrypt or passlib
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL

**Shared:**
- Token Format: JWT (JSON Web Token)
- Token Algorithm: HS256 (HMAC with SHA-256)
- Token Expiration: 1 hour
- Shared Secret: BETTER_AUTH_SECRET (environment variable)

### Architecture Decisions

**Decision 1: Token Storage - localStorage**
- **Rationale:** Simpler implementation, accessible to JavaScript for API calls
- **Tradeoff:** Vulnerable to XSS attacks vs. httpOnly cookies
- **Mitigation:** Rely on Content Security Policy and input sanitization

**Decision 2: Token Expiration - 1 Hour**
- **Rationale:** Higher security priority, limits exposure window if token stolen
- **Tradeoff:** Users must re-authenticate hourly vs. 24-hour convenience
- **Impact:** No refresh token mechanism; manual re-authentication required

**Decision 3: No Rate Limiting (Initial)**
- **Rationale:** Focus on core authentication first, defer to future iteration
- **Tradeoff:** Vulnerable to brute force attacks vs. implementation complexity
- **Mitigation:** Use generic error messages, same response times for valid/invalid users

**Decision 4: Password Complexity**
- **Requirements:** Minimum 8 characters, at least one uppercase, one lowercase, one number
- **Rationale:** Balance between security and user convenience
- **Note:** No special characters required

### Key Constraints

1. **Security-First:** Backend authentication must be complete before frontend integration
2. **Stateless:** No server-side session storage; JWT contains all auth information
3. **User Isolation:** Every API request must verify user_id matches authenticated user
4. **No Manual Coding:** All code generated via Claude Code workflows
5. **Decoupled:** Frontend and backend communicate only via REST API

### Integration Points

**Frontend → Backend:**
- Authentication endpoints: POST /auth/signup, POST /auth/signin
- Protected API endpoints: All require Authorization: Bearer <token> header
- Error handling: 401 (unauthenticated) → redirect to login, 403 (forbidden) → show error

**Backend → Database:**
- User table: user_id (PK), email (unique), password_hash, created_at, updated_at
- Row-level security: All queries filtered by authenticated user_id

**Environment Configuration:**
- BETTER_AUTH_SECRET: Shared between frontend and backend (minimum 32 characters)
- JWT_EXPIRATION_HOURS: 1 (one hour)
- DATABASE_URL: Neon PostgreSQL connection string

---

## Constitution Check

### Principle 1: Spec-Driven Development ✅
- **Compliance:** Complete specification exists at `specs/1-auth-user-isolation/spec.md`
- **Verification:** This plan derived directly from clarified specification
- **Traceability:** All implementation tasks will reference spec requirements

### Principle 2: Security-First Architecture ✅
- **Compliance:** JWT authentication mandatory for all API endpoints
- **Verification:** Backend middleware intercepts all requests before route handlers
- **User Isolation:** Authenticated user_id verified against requested resources
- **Secrets Management:** BETTER_AUTH_SECRET in environment variables only

### Principle 3: Deterministic Behavior ✅
- **Compliance:** Explicit API contracts defined (see contracts/ directory)
- **Verification:** All endpoints have defined request/response schemas
- **Error Handling:** Consistent HTTP status codes (401, 403, 400, 500)

### Principle 4: Zero Manual Coding ✅
- **Compliance:** All code generated via `/sp.implement` workflow
- **Verification:** Tasks will specify exact code generation commands
- **Manual Edits:** Limited to .env configuration only

### Principle 5: Decoupled Architecture ✅
- **Compliance:** Frontend and backend communicate only via REST API
- **Verification:** No direct database access from frontend
- **Independence:** Frontend and backend can be deployed separately

**Overall Assessment:** ✅ PASS - All constitutional principles satisfied

---

## Phase 0: Research & Design Decisions

### Research Topics

#### R1: Better Auth JWT Plugin Configuration
**Question:** How to configure Better Auth with JWT plugin in Next.js App Router?
**Research Needed:**
- Better Auth installation and setup
- JWT plugin configuration
- Token payload customization (user_id, email)
- Token expiration configuration
- localStorage integration

**Outcome:** Document exact configuration steps in research.md

#### R2: FastAPI JWT Middleware Implementation
**Question:** What's the best pattern for JWT verification middleware in FastAPI?
**Research Needed:**
- FastAPI security dependencies vs. middleware
- PyJWT vs. python-jose library comparison
- JWT signature verification with HS256
- User context injection into request lifecycle
- Error handling for invalid/expired tokens

**Outcome:** Document recommended middleware pattern in research.md

#### R3: Password Hashing Best Practices
**Question:** Which password hashing library and configuration for Python?
**Research Needed:**
- bcrypt vs. passlib comparison
- Recommended number of hashing rounds (minimum 10)
- Password validation implementation
- Secure password comparison

**Outcome:** Document chosen library and configuration in research.md

#### R4: Frontend HTTP Client with Token Injection
**Question:** How to automatically attach JWT to all API requests in Next.js?
**Research Needed:**
- Axios interceptors vs. fetch wrapper
- Token retrieval from localStorage
- Authorization header format
- 401 error handling and redirect

**Outcome:** Document HTTP client setup pattern in research.md

#### R5: User Isolation Patterns
**Question:** How to enforce user_id matching at API layer?
**Research Needed:**
- FastAPI dependency injection for authenticated user
- Route parameter validation against authenticated user
- Database query filtering by user_id
- 403 Forbidden response patterns

**Outcome:** Document user isolation enforcement pattern in research.md

### Design Decisions Summary

All research findings will be consolidated in `specs/1-auth-user-isolation/research.md` with:
- Decision made
- Rationale
- Alternatives considered
- Implementation guidance

---

## Phase 1: Data Model & API Contracts

### Data Model

See `specs/1-auth-user-isolation/data-model.md` for complete entity definitions.

**User Entity:**
```
User
├── user_id: UUID (Primary Key)
├── email: String (Unique, Not Null)
├── password_hash: String (Not Null)
├── created_at: DateTime (Not Null, Default: now())
└── updated_at: DateTime (Not Null, Default: now())

Constraints:
- email must be valid email format
- password_hash must never be exposed in API responses
- email uniqueness enforced at database level

Validation Rules:
- Email: RFC 5322 compliant
- Password (pre-hash): 8+ chars, 1 uppercase, 1 lowercase, 1 number
```

**JWT Token (Logical Entity):**
```
JWT Payload
├── user_id: UUID
├── email: String
├── exp: Unix Timestamp (issued_at + 1 hour)
└── iat: Unix Timestamp (issued_at)

Signature:
- Algorithm: HS256
- Secret: BETTER_AUTH_SECRET (from environment)
```

### API Contracts

See `specs/1-auth-user-isolation/contracts/` for OpenAPI specifications.

#### POST /auth/signup
**Purpose:** Create new user account and issue JWT token

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (201 Created):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-02-03T12:00:00Z"
  }
}
```

**Error Responses:**
- 400 Bad Request: Invalid email format or password requirements not met
- 409 Conflict: Email already exists

#### POST /auth/signin
**Purpose:** Authenticate existing user and issue JWT token

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "created_at": "2026-02-03T12:00:00Z"
  }
}
```

**Error Responses:**
- 401 Unauthorized: Invalid credentials (generic message to prevent user enumeration)

#### Protected Endpoints Pattern
**All protected endpoints require:**

**Request Header:**
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Error Responses:**
- 401 Unauthorized: Missing, invalid, or expired token
- 403 Forbidden: Valid token but insufficient permissions (user_id mismatch)

---

## Phase 2: Implementation Sequence

### Stage 1: Backend Authentication Foundation (Security-First)

**Objective:** Establish backend JWT verification before any frontend integration

#### Task 1.1: Database Schema Setup
**Description:** Create User table with proper constraints
**Acceptance Criteria:**
- User table exists with all required fields
- Email uniqueness constraint enforced
- Timestamps auto-populate
- No password field (only password_hash)

**Implementation:**
- Use SQLModel to define User model
- Create Alembic migration
- Apply migration to Neon database

#### Task 1.2: Password Hashing Utilities
**Description:** Implement secure password hashing and verification
**Acceptance Criteria:**
- Password hashing uses bcrypt/passlib with 10+ rounds
- Hash verification function available
- Password validation enforces complexity rules (8 chars, uppercase, lowercase, number)
- No plaintext passwords ever stored or logged

**Implementation:**
- Create `auth/password.py` utility module
- Functions: hash_password(), verify_password(), validate_password_strength()

#### Task 1.3: JWT Token Generation
**Description:** Implement JWT token creation with proper payload
**Acceptance Criteria:**
- Token includes user_id, email, exp, iat
- Token signed with BETTER_AUTH_SECRET from environment
- Token expiration set to 1 hour
- Token uses HS256 algorithm

**Implementation:**
- Create `auth/jwt.py` utility module
- Function: create_access_token(user_id, email) -> str

#### Task 1.4: JWT Verification Middleware
**Description:** Create FastAPI middleware to verify JWT on all requests
**Acceptance Criteria:**
- Middleware intercepts all API requests
- Verifies JWT signature using BETTER_AUTH_SECRET
- Checks token expiration
- Extracts user_id and email from payload
- Returns 401 for missing/invalid/expired tokens
- Injects authenticated user into request context

**Implementation:**
- Create `auth/middleware.py`
- Use FastAPI Depends() or middleware pattern
- Make authenticated user available via dependency injection

#### Task 1.5: User Signup Endpoint
**Description:** Implement POST /auth/signup endpoint
**Acceptance Criteria:**
- Accepts email and password
- Validates email format
- Validates password complexity
- Checks for duplicate email (returns 409)
- Hashes password before storage
- Creates user record
- Generates and returns JWT token
- Returns user object (without password_hash)

**Implementation:**
- Create `routes/auth.py`
- Endpoint: POST /auth/signup
- Use password and JWT utilities

#### Task 1.6: User Signin Endpoint
**Description:** Implement POST /auth/signin endpoint
**Acceptance Criteria:**
- Accepts email and password
- Looks up user by email
- Verifies password hash
- Returns 401 with generic message on failure
- Generates and returns JWT token on success
- Returns user object (without password_hash)
- Same response time for valid/invalid users (timing attack prevention)

**Implementation:**
- Add to `routes/auth.py`
- Endpoint: POST /auth/signin
- Use password verification utility

#### Task 1.7: User Isolation Enforcement
**Description:** Implement user_id verification for protected routes
**Acceptance Criteria:**
- Authenticated user_id available in all route handlers
- Route handlers can access current_user via dependency
- Mismatched user_id returns 403 Forbidden
- Database queries automatically filtered by user_id

**Implementation:**
- Create `auth/dependencies.py`
- Function: get_current_user() -> User
- Use in route dependencies: Depends(get_current_user)

#### Task 1.8: Backend Integration Testing
**Description:** Test backend authentication flow end-to-end
**Acceptance Criteria:**
- Signup creates user and returns valid token
- Signin authenticates and returns valid token
- Protected endpoint with valid token succeeds
- Protected endpoint without token returns 401
- Protected endpoint with expired token returns 401
- Protected endpoint with invalid token returns 401
- Cross-user access attempt returns 403

**Implementation:**
- Create `tests/test_auth.py`
- Use pytest with FastAPI TestClient
- Test all success and failure scenarios

### Stage 2: Frontend Authentication Integration

**Objective:** Integrate Better Auth with backend JWT system

#### Task 2.1: Better Auth Installation
**Description:** Install and configure Better Auth in Next.js
**Acceptance Criteria:**
- Better Auth installed via npm/yarn
- JWT plugin enabled
- Configuration file created
- Environment variables configured

**Implementation:**
- Install: `npm install better-auth`
- Create `lib/auth.ts` configuration
- Configure JWT plugin with BETTER_AUTH_SECRET

#### Task 2.2: Authentication Provider Setup
**Description:** Configure email/password authentication provider
**Acceptance Criteria:**
- Email/password provider enabled
- JWT payload includes user_id and email
- Token expiration set to 1 hour
- Token stored in localStorage

**Implementation:**
- Configure provider in `lib/auth.ts`
- Set JWT payload structure
- Configure token storage mechanism

#### Task 2.3: Signup Page Implementation
**Description:** Create user signup page with form
**Acceptance Criteria:**
- Signup form with email and password fields
- Client-side validation (email format, password complexity)
- Calls Better Auth signup method
- Stores JWT token in localStorage on success
- Redirects to authenticated area on success
- Displays error messages on failure

**Implementation:**
- Create `app/signup/page.tsx`
- Use Better Auth signup hook
- Form validation with react-hook-form or native

#### Task 2.4: Signin Page Implementation
**Description:** Create user signin page with form
**Acceptance Criteria:**
- Signin form with email and password fields
- Calls Better Auth signin method
- Stores JWT token in localStorage on success
- Redirects to authenticated area on success
- Displays error messages on failure

**Implementation:**
- Create `app/signin/page.tsx`
- Use Better Auth signin hook
- Form validation

#### Task 2.5: API Client with Token Injection
**Description:** Create centralized API client that attaches JWT to requests
**Acceptance Criteria:**
- All API calls go through centralized client
- JWT automatically retrieved from localStorage
- Authorization header automatically attached (Bearer <token>)
- 401 responses trigger redirect to signin page
- 403 responses display error message

**Implementation:**
- Create `lib/api-client.ts`
- Use Axios interceptors or fetch wrapper
- Handle authentication errors globally

#### Task 2.6: Authentication Context Provider
**Description:** Create React context for authentication state
**Acceptance Criteria:**
- Provides current user information
- Provides authentication status (loading, authenticated, unauthenticated)
- Provides logout function
- Clears token from localStorage on logout

**Implementation:**
- Create `contexts/AuthContext.tsx`
- Wrap app with AuthProvider
- Expose useAuth() hook

#### Task 2.7: Protected Route Component
**Description:** Create component to protect authenticated routes
**Acceptance Criteria:**
- Checks authentication status
- Redirects to signin if unauthenticated
- Shows loading state while checking
- Allows access if authenticated

**Implementation:**
- Create `components/ProtectedRoute.tsx`
- Use AuthContext to check status
- Redirect with next router

#### Task 2.8: Frontend Integration Testing
**Description:** Test frontend authentication flow end-to-end
**Acceptance Criteria:**
- User can signup and is redirected to authenticated area
- User can signin and is redirected to authenticated area
- Token is stored in localStorage
- Protected routes redirect unauthenticated users
- API calls include Authorization header
- Expired token triggers re-authentication
- Logout clears token and redirects to signin

**Implementation:**
- Create `tests/auth.test.tsx`
- Use React Testing Library
- Mock API responses
- Test all user flows

### Stage 3: End-to-End Validation

**Objective:** Verify complete authentication system works across frontend and backend

#### Task 3.1: Integration Test Suite
**Description:** Create comprehensive integration tests
**Test Scenarios:**
1. New user signup → token issued → API call succeeds
2. Existing user signin → token issued → API call succeeds
3. API call without token → 401 → redirect to signin
4. API call with expired token → 401 → redirect to signin
5. API call with invalid token → 401 → redirect to signin
6. User A attempts to access User B's resource → 403
7. Token expires during session → next API call fails → redirect to signin
8. Logout → token cleared → protected route redirects to signin

**Acceptance Criteria:**
- All 8 scenarios pass
- No manual intervention required
- Tests run in CI/CD pipeline

#### Task 3.2: Security Audit
**Description:** Verify security requirements are met
**Audit Checklist:**
- [ ] All API endpoints require authentication
- [ ] JWT signature verified on every request
- [ ] Token expiration enforced
- [ ] User isolation prevents cross-user access
- [ ] Password hashing uses 10+ rounds
- [ ] No passwords in logs or error messages
- [ ] BETTER_AUTH_SECRET not committed to version control
- [ ] Generic error messages prevent user enumeration
- [ ] Same response time for valid/invalid credentials

**Acceptance Criteria:**
- All checklist items verified
- No security vulnerabilities found

#### Task 3.3: Performance Validation
**Description:** Verify authentication performance meets requirements
**Performance Targets:**
- Token verification: < 10ms per request
- Signup: < 500ms
- Signin: < 500ms
- Middleware overhead: < 5ms per request

**Acceptance Criteria:**
- All performance targets met
- No database queries required for token verification

#### Task 3.4: Documentation
**Description:** Create quickstart guide for authentication system
**Content:**
- Environment variable setup (BETTER_AUTH_SECRET)
- How to protect new API endpoints
- How to access authenticated user in route handlers
- How to create protected frontend routes
- Troubleshooting common issues

**Acceptance Criteria:**
- Quickstart guide created at `specs/1-auth-user-isolation/quickstart.md`
- All setup steps documented
- Code examples provided

---

## Phase 3: Deployment Preparation

### Environment Configuration

**Required Environment Variables:**

**Backend (.env):**
```
BETTER_AUTH_SECRET=<32+ character random string>
JWT_EXPIRATION_HOURS=1
DATABASE_URL=<Neon PostgreSQL connection string>
```

**Frontend (.env.local):**
```
NEXT_PUBLIC_API_URL=<Backend API URL>
BETTER_AUTH_SECRET=<same as backend>
```

**Security Notes:**
- BETTER_AUTH_SECRET must be identical in frontend and backend
- Generate secret with: `openssl rand -base64 32`
- Never commit .env files to version control
- Use different secrets for development and production

### Deployment Checklist

- [ ] Database migrations applied to production database
- [ ] Environment variables configured in deployment platform
- [ ] BETTER_AUTH_SECRET matches between frontend and backend
- [ ] CORS configured to allow frontend domain
- [ ] HTTPS enforced for all authentication endpoints
- [ ] Frontend and backend deployed independently
- [ ] Health check endpoints responding
- [ ] Integration tests passing against production environment

---

## Success Criteria

The Authentication & User Isolation feature is complete when:

1. ✅ Users can signup with email and password
2. ✅ Users can signin with email and password
3. ✅ JWT token issued on successful authentication
4. ✅ JWT token stored in localStorage
5. ✅ All API requests include Authorization header
6. ✅ Backend verifies JWT on every request
7. ✅ Invalid/missing/expired tokens return 401
8. ✅ Cross-user access attempts return 403
9. ✅ User isolation enforced at API layer
10. ✅ Token expires after 1 hour
11. ✅ Expired token triggers re-authentication
12. ✅ All integration tests passing
13. ✅ Security audit checklist complete
14. ✅ Performance targets met
15. ✅ Documentation complete

---

## Risk Mitigation

### Risk 1: Token Mismatch Between Frontend and Backend
**Mitigation Implemented:**
- Startup validation checks BETTER_AUTH_SECRET is configured
- Integration tests verify end-to-end token flow
- Documentation emphasizes secret must match

### Risk 2: XSS Token Theft (localStorage)
**Mitigation Implemented:**
- Content Security Policy configured
- Input sanitization on all user inputs
- Token expiration limited to 1 hour
- Documentation warns about XSS risks

### Risk 3: Brute Force Attacks (No Rate Limiting)
**Mitigation Implemented:**
- Generic error messages prevent user enumeration
- Same response time for valid/invalid users
- Documented as future enhancement
- Password complexity requirements reduce attack surface

### Risk 4: Token Expiration UX Impact
**Mitigation Implemented:**
- Clear error messages when token expires
- Automatic redirect to signin page
- Documentation explains 1-hour expiration policy
- Future enhancement: consider refresh tokens

---

## Future Enhancements

**Not in scope for initial implementation, but documented for future iterations:**

1. **Rate Limiting:** Implement rate limiting on authentication endpoints (5 attempts per 15 minutes)
2. **Refresh Tokens:** Add refresh token mechanism to avoid hourly re-authentication
3. **Password Reset:** Email-based password reset flow
4. **Email Verification:** Verify email addresses before account activation
5. **Multi-Factor Authentication:** Add MFA support for enhanced security
6. **OAuth Integration:** Support social login (Google, GitHub, etc.)
7. **Session Management:** Track active sessions and allow remote logout
8. **httpOnly Cookies:** Migrate from localStorage to httpOnly cookies for better XSS protection
9. **Token Revocation:** Implement token blacklist for immediate logout
10. **Audit Logging:** Log all authentication events for security monitoring

---

## Appendix

### Technology References

**Better Auth:**
- Documentation: https://www.better-auth.com/
- JWT Plugin: https://www.better-auth.com/docs/plugins/jwt

**FastAPI Security:**
- Documentation: https://fastapi.tiangolo.com/tutorial/security/
- JWT Tutorial: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

**PyJWT:**
- Documentation: https://pyjwt.readthedocs.io/
- HS256 Algorithm: https://pyjwt.readthedocs.io/en/stable/usage.html#encoding-decoding-tokens-with-hs256

**Password Hashing:**
- bcrypt: https://github.com/pyca/bcrypt/
- passlib: https://passlib.readthedocs.io/

### Related Documents

- Feature Specification: `specs/1-auth-user-isolation/spec.md`
- Data Model: `specs/1-auth-user-isolation/data-model.md`
- API Contracts: `specs/1-auth-user-isolation/contracts/`
- Research Findings: `specs/1-auth-user-isolation/research.md`
- Quickstart Guide: `specs/1-auth-user-isolation/quickstart.md`
- Project Constitution: `.specify/memory/constitution.md`

---

**End of Implementation Plan**
