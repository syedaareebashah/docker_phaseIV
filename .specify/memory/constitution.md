<!--
Sync Impact Report:
- Version: 1.0.0 (Initial constitution for Todo Full-Stack Web Application)
- Modified principles: N/A (new constitution)
- Added sections: All sections (initial creation)
- Removed sections: N/A
- Templates requiring updates: ⚠ pending (templates to be created)
- Follow-up TODOs: Create plan-template.md, spec-template.md, tasks-template.md
-->

# Project Constitution

**Project Name:** Todo Full-Stack Web Application (Hackathon Phase 2)

**Version:** 1.0.0
**Ratification Date:** 2026-02-03
**Last Amended Date:** 2026-02-03

---

## Purpose

This constitution establishes the foundational principles, standards, and constraints for the Todo Full-Stack Web Application project. It serves as the authoritative reference for all development decisions and ensures consistency across the entire development lifecycle.

---

## Core Principles

### Principle 1: Spec-Driven Development

**Statement:** All development MUST follow the spec → plan → tasks → implementation workflow. No code shall be written without a corresponding specification and implementation plan.

**Rationale:** Spec-driven development ensures that all features are properly designed, reviewed, and understood before implementation begins. This reduces rework, prevents scope creep, and maintains architectural consistency.

**Requirements:**
- Every feature MUST have a complete specification in `specs/<feature>/spec.md`
- Every specification MUST have an architectural plan in `specs/<feature>/plan.md`
- Every plan MUST be broken down into testable tasks in `specs/<feature>/tasks.md`
- Implementation MUST NOT begin until spec, plan, and tasks are approved
- All changes MUST be traceable back to a requirement in the spec

### Principle 2: Security-First Architecture

**Statement:** Security MUST be embedded at every layer of the application. JWT-based authentication and user isolation are mandatory for all API endpoints.

**Rationale:** Security vulnerabilities can compromise user data and system integrity. By enforcing security at the architectural level, we prevent entire classes of vulnerabilities rather than patching individual issues.

**Requirements:**
- ALL API endpoints MUST require JWT authentication (no exceptions)
- JWT verification MUST be stateless and middleware-based
- User data MUST be isolated at the database layer (row-level security)
- Task ownership MUST be enforced at both database and API layers
- Shared secret (BETTER_AUTH_SECRET) MUST be stored in environment variables only
- No credentials or secrets MUST ever be committed to version control
- All authentication flows MUST use Better Auth with JWT plugin

### Principle 3: Deterministic Behavior

**Statement:** The application MUST exhibit predictable, consistent behavior across all operations. API contracts MUST be explicit and strictly enforced.

**Rationale:** Deterministic systems are easier to test, debug, and reason about. Clear contracts prevent integration issues and reduce cognitive load for developers.

**Requirements:**
- All API endpoints MUST have explicit request/response schemas
- Error responses MUST follow a consistent format with appropriate HTTP status codes
- Database operations MUST be transactional where appropriate
- State changes MUST be atomic and idempotent where possible
- API behavior MUST be documented and tested
- No implicit assumptions or "magic" behavior allowed

### Principle 4: Zero Manual Coding

**Statement:** All code MUST be generated through Claude Code and Spec-Kit Plus workflows. Manual code editing is prohibited except for configuration files.

**Rationale:** Automated code generation ensures consistency, reduces human error, and maintains traceability between specifications and implementation.

**Requirements:**
- All feature code MUST be generated via `/sp.implement` or equivalent commands
- Manual edits MUST be limited to `.env`, configuration files, and documentation
- All code changes MUST be traceable to a task in `tasks.md`
- Code reviews MUST verify adherence to generated patterns
- Deviations from generated code MUST be documented with justification

### Principle 5: Decoupled Architecture

**Statement:** Frontend and backend MUST be completely decoupled and communicate exclusively via REST API. No direct database access from frontend is permitted.

**Rationale:** Decoupling enables independent development, testing, and deployment of frontend and backend. It also enforces security boundaries and enables future scalability.

**Requirements:**
- Frontend MUST NOT have direct database access
- All data exchange MUST occur through REST API endpoints
- Frontend and backend MUST be deployable independently
- API contracts MUST be versioned and backward compatible
- Cross-origin requests MUST be properly configured with CORS

---

## Technology Standards

### Frontend Stack

- **Framework:** Next.js 16+ (App Router only)
- **Routing:** App Router (no Pages Router)
- **Styling:** Tailwind CSS (or as specified in project)
- **State Management:** React hooks and context (or as specified)
- **Authentication:** Better Auth client integration

### Backend Stack

- **Framework:** Python FastAPI
- **ORM:** SQLModel
- **Database:** Neon Serverless PostgreSQL
- **Authentication:** Better Auth with JWT plugin
- **API Documentation:** OpenAPI/Swagger (auto-generated by FastAPI)

### Development Tools

- **Version Control:** Git
- **Code Generation:** Claude Code + Spec-Kit Plus
- **Environment Management:** `.env` files (never committed)
- **Testing:** pytest (backend), Jest/React Testing Library (frontend)

---

## Quality Requirements

### API Standards

- REST endpoints MUST follow HTTP semantics:
  - GET: Retrieve resources (idempotent, no side effects)
  - POST: Create resources
  - PUT/PATCH: Update resources
  - DELETE: Remove resources
- Status codes MUST be semantically correct:
  - 200: Success
  - 201: Created
  - 400: Bad Request (client error)
  - 401: Unauthorized (authentication required)
  - 403: Forbidden (insufficient permissions)
  - 404: Not Found
  - 500: Internal Server Error
- All endpoints MUST return consistent JSON response format
- Error responses MUST include meaningful error messages

### Code Quality

- Code MUST be generated through approved workflows
- All functions MUST have clear, single responsibilities
- Error handling MUST be explicit and comprehensive
- No hardcoded values (use environment variables or configuration)
- Code MUST be self-documenting with clear naming

### Testing Requirements

- All API endpoints MUST have integration tests
- Authentication flows MUST be tested end-to-end
- Database operations MUST be tested with rollback
- Frontend components MUST have unit tests for critical logic
- Test coverage MUST be tracked and maintained

### Security Requirements

- JWT tokens MUST have appropriate expiration times
- Passwords MUST be hashed (never stored in plaintext)
- SQL injection MUST be prevented (use parameterized queries via ORM)
- XSS MUST be prevented (proper input sanitization and output encoding)
- CSRF protection MUST be implemented where applicable
- Rate limiting MUST be implemented on authentication endpoints

---

## Constraints

### Mandatory Constraints

1. **Authentication:** ALL API endpoints MUST require JWT authentication
2. **User Isolation:** Task ownership MUST be enforced at database and API layers
3. **No Direct DB Access:** Frontend MUST NOT access database directly
4. **Stateless JWT:** JWT verification MUST be stateless and middleware-based
5. **Environment Variables:** BETTER_AUTH_SECRET MUST be in environment variables only

### Technology Constraints

1. Frontend MUST use Next.js 16+ with App Router (no Pages Router)
2. Backend MUST use Python FastAPI
3. ORM MUST be SQLModel
4. Database MUST be Neon Serverless PostgreSQL
5. Authentication MUST use Better Auth with JWT plugin

### Process Constraints

1. All features MUST follow spec → plan → tasks → implementation
2. No manual coding except configuration files
3. All code MUST be generated via Claude Code + Spec-Kit Plus
4. All changes MUST be traceable to specifications

---

## Governance

### Amendment Process

1. Proposed amendments MUST be documented with rationale
2. Amendments MUST be reviewed for impact on existing specifications
3. Version MUST be incremented according to semantic versioning:
   - **MAJOR:** Backward-incompatible changes to principles or constraints
   - **MINOR:** New principles or sections added
   - **PATCH:** Clarifications, wording improvements, non-semantic changes
4. `LAST_AMENDED_DATE` MUST be updated to current date
5. Sync Impact Report MUST be generated and prepended as HTML comment

### Versioning Policy

- Constitution version follows semantic versioning (MAJOR.MINOR.PATCH)
- All dependent templates MUST be reviewed when constitution changes
- Breaking changes MUST be communicated to all stakeholders
- Version history MUST be maintained in git commits

### Compliance Review

- All specifications MUST reference this constitution
- All architectural decisions MUST align with core principles
- Code reviews MUST verify adherence to standards
- Violations MUST be documented and justified or corrected

### Dependent Artifacts

The following artifacts MUST remain consistent with this constitution:

- `.specify/templates/plan-template.md` - Architecture planning template
- `.specify/templates/spec-template.md` - Feature specification template
- `.specify/templates/tasks-template.md` - Task breakdown template
- `.specify/templates/commands/*.md` - Command definitions
- `README.md` - Project documentation
- All feature specifications in `specs/*/spec.md`

---

## Success Criteria

A feature is considered complete when:

1. ✅ Specification exists and is approved
2. ✅ Architectural plan exists and is approved
3. ✅ Tasks are defined with acceptance criteria
4. ✅ All tasks are implemented and tested
5. ✅ All tests pass
6. ✅ Code adheres to all principles and standards
7. ✅ Authentication and authorization are properly enforced
8. ✅ API contracts are documented and tested
9. ✅ No manual code edits outside approved scope
10. ✅ Changes are traceable to requirements

---

**End of Constitution**
