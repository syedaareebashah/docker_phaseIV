# Implementation Plan: Backend Task Management API

**Feature ID:** 2-backend-task-api
**Version:** 1.0.0
**Status:** Draft
**Created:** 2026-02-03
**Last Updated:** 2026-02-03

---

## Executive Summary

This plan outlines the implementation strategy for the Backend Task Management API, providing secure CRUD operations for user tasks with strict ownership enforcement. The implementation builds directly on Feature 1 (Authentication & User Isolation) and reuses its authentication infrastructure.

**Key Objectives:**
- Implement RESTful task management API with 6 endpoints
- Enforce user ownership at database query level
- Integrate seamlessly with existing authentication system
- Maintain complete user data isolation
- Provide deterministic, stateless API behavior

**Implementation Approach:**
- Database-first: Schema and models before endpoints
- Reuse authentication: Leverage Feature 1's user context
- Query-level isolation: Filter by user_id in all database queries
- Comprehensive validation: Request data and ownership checks
- Zero manual coding: Claude Code + Spec-Kit Plus only

---

## Technical Context

### Technology Stack

**Backend Framework:**
- Framework: FastAPI
- ORM: SQLModel
- Database: Neon Serverless PostgreSQL
- Migration Tool: Alembic
- Validation: Pydantic (built into FastAPI/SQLModel)

**Dependencies from Feature 1:**
- Authentication middleware/dependencies
- JWT token verification
- User context extraction (get_current_user)
- User model and database session

**New Components:**
- Task model (SQLModel)
- Task routes (FastAPI router)
- Task-specific validation logic

### Architecture Decisions

**Decision 1: Reuse Feature 1 Authentication**
- **Rationale:** Feature 1 provides complete authentication infrastructure
- **Implementation:** Import get_current_user dependency, use in all task routes
- **Benefit:** No duplication, consistent security across features

**Decision 2: User ID in Route Path**
- **Rationale:** RESTful convention, explicit resource ownership
- **Implementation:** Routes like /api/{user_id}/tasks
- **Validation:** Verify route user_id matches authenticated user_id

**Decision 3: Query-Level Filtering**
- **Rationale:** Defense in depth, prevent data leakage at database level
- **Implementation:** All task queries include WHERE user_id = authenticated_user_id
- **Benefit:** Even if route validation fails, database won't return wrong data

**Decision 4: Automatic Timestamps**
- **Rationale:** Consistent, reliable timestamp management
- **Implementation:** SQLModel default_factory for created_at/updated_at
- **Benefit:** No manual timestamp management, prevents errors

**Decision 5: Soft Completion Toggle**
- **Rationale:** Simple boolean toggle is sufficient for MVP
- **Implementation:** PATCH endpoint toggles completed field
- **Future:** Can extend to support explicit true/false values

### Key Constraints

1. **Feature 1 Dependency:** Authentication system must be fully operational
2. **User Isolation:** All queries must filter by authenticated user_id
3. **Stateless:** No server-side session state for tasks
4. **ORM Only:** No raw SQL queries (security and maintainability)
5. **RESTful:** Follow HTTP semantics strictly

### Integration Points

**Feature 1 → Feature 2:**
- Authentication dependency: get_current_user()
- User model: User entity with user_id
- Database session: Shared session management
- Error responses: Consistent 401/403 handling

**Database Schema:**
- tasks table with foreign key to users table
- user_id indexed for fast filtering
- Timestamps for audit trail

**Environment Configuration:**
- DATABASE_URL: Shared with Feature 1 (same database)
- No additional environment variables needed

---

## Constitution Check

### Principle 1: Spec-Driven Development ✅
- **Compliance:** Complete specification exists at `specs/2-backend-task-api/spec.md`
- **Verification:** This plan derived directly from specification
- **Traceability:** All implementation tasks reference spec requirements

### Principle 2: Security-First Architecture ✅
- **Compliance:** All endpoints require authentication (via Feature 1)
- **Verification:** User isolation enforced at query level
- **Ownership:** Every task operation validates ownership
- **Data Protection:** No cross-user data access possible

### Principle 3: Deterministic Behavior ✅
- **Compliance:** Explicit API contracts defined (see contracts/ directory)
- **Verification:** All endpoints have defined request/response schemas
- **Error Handling:** Consistent HTTP status codes (404, 403, 400, 500)
- **Predictability:** Same input always produces same output

### Principle 4: Zero Manual Coding ✅
- **Compliance:** All code generated via `/sp.implement` workflow
- **Verification:** Tasks specify exact code generation commands
- **Manual Edits:** None required (configuration handled by Feature 1)

### Principle 5: Decoupled Architecture ✅
- **Compliance:** Backend API only, no frontend coupling
- **Verification:** RESTful API can be consumed by any client
- **Independence:** Task API deployable independently (with Feature 1)

**Overall Assessment:** ✅ PASS - All constitutional principles satisfied

---

## Phase 0: Research & Design Decisions

### Research Topics

All research topics for backend development were covered in Feature 1:
- FastAPI patterns and best practices
- SQLModel ORM usage
- Database connection management
- Dependency injection patterns
- Error handling strategies

**New Research Needed:**

#### R1: SQLModel Relationships and Foreign Keys
**Question:** How to define foreign key relationship between Task and User in SQLModel?
**Research Needed:**
- Foreign key syntax in SQLModel
- Relationship definition (Task belongs to User)
- Cascade delete behavior
- Index creation for foreign keys

**Outcome:** Document in research.md

#### R2: RESTful Route Design for Nested Resources
**Question:** Best practices for user-scoped resource routes?
**Research Needed:**
- Route patterns: /api/{user_id}/tasks vs /api/tasks
- Path parameter validation
- RESTful conventions for nested resources

**Outcome:** Document in research.md

#### R3: Partial Update Patterns (PATCH vs PUT)
**Question:** When to use PATCH vs PUT for updates?
**Research Needed:**
- PATCH for partial updates (completion toggle)
- PUT for full resource replacement
- FastAPI implementation patterns

**Outcome:** Document in research.md

---

## Phase 1: Data Model & API Contracts

### Data Model

See `specs/2-backend-task-api/data-model.md` for complete entity definitions.

**Task Entity:**
```
Task
├── id: UUID (Primary Key)
├── user_id: UUID (Foreign Key → User.user_id)
├── title: String (Not Null, Max 255 chars)
├── description: String (Nullable, Max 1000 chars)
├── completed: Boolean (Not Null, Default: false)
├── created_at: DateTime (Not Null, Default: now())
└── updated_at: DateTime (Not Null, Default: now())

Constraints:
- user_id must reference existing user
- title cannot be empty string
- Foreign key indexed for fast filtering

Validation Rules:
- title: Required, 1-255 characters
- description: Optional, 0-1000 characters
- completed: Boolean only
```

### API Contracts

See `specs/2-backend-task-api/contracts/` for OpenAPI specifications.

#### GET /api/{user_id}/tasks
**Purpose:** Retrieve all tasks for authenticated user

**Path Parameters:**
- user_id: UUID (must match authenticated user)

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "completed": false,
    "created_at": "2026-02-03T12:00:00Z",
    "updated_at": "2026-02-03T12:00:00Z"
  }
]
```

**Error Responses:**
- 401: Unauthorized (no valid token)
- 403: Forbidden (user_id mismatch)

#### POST /api/{user_id}/tasks
**Purpose:** Create new task for authenticated user

**Path Parameters:**
- user_id: UUID (must match authenticated user)

**Request Body:**
```json
{
  "title": "New task",
  "description": "Optional description"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "New task",
  "description": "Optional description",
  "completed": false,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

**Error Responses:**
- 400: Bad Request (validation error)
- 401: Unauthorized
- 403: Forbidden

#### GET /api/{user_id}/tasks/{task_id}
**Purpose:** Retrieve single task by ID

**Path Parameters:**
- user_id: UUID (must match authenticated user)
- task_id: UUID

**Response (200 OK):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "completed": false,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

**Error Responses:**
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

#### PUT /api/{user_id}/tasks/{task_id}
**Purpose:** Update task fields

**Path Parameters:**
- user_id: UUID (must match authenticated user)
- task_id: UUID

**Request Body:**
```json
{
  "title": "Updated title",
  "description": "Updated description",
  "completed": true
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Updated title",
  "description": "Updated description",
  "completed": true,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:05:00Z"
}
```

**Error Responses:**
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

#### DELETE /api/{user_id}/tasks/{task_id}
**Purpose:** Delete task permanently

**Path Parameters:**
- user_id: UUID (must match authenticated user)
- task_id: UUID

**Response (204 No Content):**
```
(empty body)
```

**Error Responses:**
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

#### PATCH /api/{user_id}/tasks/{task_id}/complete
**Purpose:** Toggle task completion status

**Path Parameters:**
- user_id: UUID (must match authenticated user)
- task_id: UUID

**Response (200 OK):**
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "Task title",
  "description": "Task description",
  "completed": true,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:10:00Z"
}
```

**Error Responses:**
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

---

## Phase 2: Implementation Sequence

### Stage 1: Database Schema & Models

**Objective:** Establish task data model and database schema

#### Task 1.1: Define Task SQLModel
**Description:** Create Task model with all required fields and relationships

**Acceptance Criteria:**
- Task model defined using SQLModel
- All fields present (id, user_id, title, description, completed, timestamps)
- Foreign key relationship to User model
- Automatic UUID generation for id
- Automatic timestamp management
- Validation rules enforced (title required, max lengths)

**Implementation:**
- Create `models/task.py`
- Define Task class inheriting from SQLModel
- Configure foreign key to users table
- Set up default values and validators

#### Task 1.2: Create Database Migration
**Description:** Generate Alembic migration for tasks table

**Acceptance Criteria:**
- Migration file created
- Creates tasks table with all columns
- Foreign key constraint to users table
- Indexes on user_id and id
- Timestamps have defaults
- Migration is reversible (downgrade works)

**Implementation:**
- Run: `alembic revision --autogenerate -m "create_tasks_table"`
- Review generated migration
- Test upgrade and downgrade

#### Task 1.3: Apply Database Migration
**Description:** Apply migration to create tasks table in database

**Acceptance Criteria:**
- Migration applied successfully
- tasks table exists in database
- Foreign key constraint active
- Indexes created
- Can insert test task record

**Implementation:**
- Run: `alembic upgrade head`
- Verify table structure in database
- Test foreign key constraint

### Stage 2: Authentication Integration

**Objective:** Integrate with Feature 1 authentication system

#### Task 2.1: Import Authentication Dependencies
**Description:** Import and configure authentication dependencies from Feature 1

**Acceptance Criteria:**
- get_current_user dependency imported
- User model imported
- Database session dependency imported
- No import errors
- Dependencies available for use in routes

**Implementation:**
- Import from `auth.dependencies`
- Import from `models.user`
- Import from `database`

#### Task 2.2: Create User ID Validation Utility
**Description:** Create utility to validate route user_id matches authenticated user

**Acceptance Criteria:**
- Function accepts route user_id and authenticated user
- Returns 403 if IDs don't match
- Returns silently if IDs match
- Reusable across all endpoints

**Implementation:**
- Create `utils/validation.py`
- Function: validate_user_access(route_user_id, current_user)

### Stage 3: CRUD Endpoint Implementation

**Objective:** Implement all 6 task API endpoints

#### Task 3.1: Implement GET /api/{user_id}/tasks
**Description:** Endpoint to list all tasks for authenticated user

**Acceptance Criteria:**
- Endpoint accepts user_id path parameter
- Validates user_id matches authenticated user
- Queries tasks filtered by user_id
- Returns list of tasks (empty list if none)
- Returns 403 if user_id mismatch
- Returns 401 if not authenticated

**Implementation:**
- Create `routes/tasks.py`
- Define GET endpoint
- Use get_current_user dependency
- Query: session.query(Task).filter(Task.user_id == current_user.user_id)

#### Task 3.2: Implement POST /api/{user_id}/tasks
**Description:** Endpoint to create new task

**Acceptance Criteria:**
- Endpoint accepts user_id path parameter
- Accepts title (required) and description (optional) in body
- Validates user_id matches authenticated user
- Validates title is non-empty
- Creates task with authenticated user as owner
- Returns created task with 201 status
- Returns 400 for validation errors
- Returns 403 if user_id mismatch

**Implementation:**
- Define POST endpoint
- Create Pydantic model for request body
- Validate input
- Create Task instance with user_id from current_user
- Save to database
- Return created task

#### Task 3.3: Implement GET /api/{user_id}/tasks/{task_id}
**Description:** Endpoint to retrieve single task by ID

**Acceptance Criteria:**
- Endpoint accepts user_id and task_id path parameters
- Validates user_id matches authenticated user
- Looks up task by task_id
- Verifies task belongs to authenticated user
- Returns task if found and owned
- Returns 404 if task not found
- Returns 403 if task belongs to different user

**Implementation:**
- Define GET endpoint with task_id parameter
- Query task by ID
- Verify task.user_id == current_user.user_id
- Return task or appropriate error

#### Task 3.4: Implement PUT /api/{user_id}/tasks/{task_id}
**Description:** Endpoint to update task fields

**Acceptance Criteria:**
- Endpoint accepts user_id and task_id path parameters
- Accepts title, description, completed in body (all optional)
- Validates user_id matches authenticated user
- Looks up task by task_id
- Verifies task ownership
- Updates specified fields only
- Updates updated_at timestamp
- Returns updated task
- Returns 404 if task not found
- Returns 403 if not owned
- Returns 400 for validation errors

**Implementation:**
- Define PUT endpoint
- Create Pydantic model for request body (all fields optional)
- Look up task
- Verify ownership
- Update fields
- Update timestamp
- Save and return

#### Task 3.5: Implement DELETE /api/{user_id}/tasks/{task_id}
**Description:** Endpoint to delete task

**Acceptance Criteria:**
- Endpoint accepts user_id and task_id path parameters
- Validates user_id matches authenticated user
- Looks up task by task_id
- Verifies task ownership
- Deletes task from database
- Returns 204 No Content
- Returns 404 if task not found
- Returns 403 if not owned

**Implementation:**
- Define DELETE endpoint
- Look up task
- Verify ownership
- Delete from database
- Return 204 status

#### Task 3.6: Implement PATCH /api/{user_id}/tasks/{task_id}/complete
**Description:** Endpoint to toggle task completion status

**Acceptance Criteria:**
- Endpoint accepts user_id and task_id path parameters
- Validates user_id matches authenticated user
- Looks up task by task_id
- Verifies task ownership
- Toggles completed field (true ↔ false)
- Updates updated_at timestamp
- Returns updated task
- Returns 404 if task not found
- Returns 403 if not owned

**Implementation:**
- Define PATCH endpoint
- Look up task
- Verify ownership
- Toggle: task.completed = not task.completed
- Update timestamp
- Save and return

### Stage 4: Error Handling & Validation

**Objective:** Ensure robust error handling and input validation

#### Task 4.1: Implement Request Validation
**Description:** Add comprehensive input validation for all endpoints

**Acceptance Criteria:**
- Title validation: non-empty, max 255 characters
- Description validation: max 1000 characters
- UUID validation for path parameters
- Validation errors return 400 with descriptive messages
- Validation occurs before database operations

**Implementation:**
- Use Pydantic validators in request models
- Add custom validators for business rules
- Return FastAPI ValidationError responses

#### Task 4.2: Implement Error Response Formatting
**Description:** Ensure consistent error response format

**Acceptance Criteria:**
- All errors return JSON with "detail" field
- HTTP status codes are semantically correct
- Error messages are descriptive but don't leak sensitive info
- Consistent format across all endpoints

**Implementation:**
- Use FastAPI HTTPException
- Create error response models
- Test all error scenarios

#### Task 4.3: Add Logging
**Description:** Add logging for debugging and monitoring

**Acceptance Criteria:**
- Log all task operations (create, update, delete)
- Log authentication failures
- Log validation errors
- No sensitive data in logs (no passwords, tokens)

**Implementation:**
- Configure Python logging
- Add log statements at key points
- Test log output

### Stage 5: Testing & Validation

**Objective:** Verify all functionality works correctly

#### Task 5.1: Unit Tests for Task Model
**Description:** Test Task model validation and behavior

**Acceptance Criteria:**
- Test task creation with valid data
- Test validation errors (empty title, too long fields)
- Test default values (completed=false, timestamps)
- Test foreign key constraint

**Implementation:**
- Create `tests/test_task_model.py`
- Use pytest
- Test all validation rules

#### Task 5.2: Integration Tests for Task API
**Description:** Test all endpoints end-to-end

**Test Scenarios:**
1. Create task → verify in database
2. List tasks → verify only user's tasks returned
3. Get single task → verify correct task returned
4. Update task → verify changes persisted
5. Delete task → verify removed from database
6. Toggle completion → verify status changed
7. Cross-user access → verify 403 returned
8. Non-existent task → verify 404 returned

**Acceptance Criteria:**
- All 8 scenarios pass
- Tests use real database (test database)
- Tests clean up after themselves
- Tests run in CI/CD pipeline

**Implementation:**
- Create `tests/test_task_api.py`
- Use FastAPI TestClient
- Create test fixtures for users and tasks
- Test all success and failure paths

#### Task 5.3: User Isolation Verification
**Description:** Verify users cannot access each other's tasks

**Test Scenarios:**
1. User A creates task
2. User B attempts to list User A's tasks → empty list
3. User B attempts to get User A's task → 403
4. User B attempts to update User A's task → 403
5. User B attempts to delete User A's task → 403

**Acceptance Criteria:**
- All cross-user access attempts blocked
- No data leakage in error responses
- User isolation maintained at query level

**Implementation:**
- Create multi-user test scenarios
- Verify database queries filter correctly
- Test with multiple concurrent users

#### Task 5.4: Performance Testing
**Description:** Verify performance meets requirements

**Performance Targets:**
- Task creation: < 200ms
- Task list retrieval: < 500ms (up to 1000 tasks)
- Single task retrieval: < 100ms
- Task update: < 200ms
- Task deletion: < 200ms

**Acceptance Criteria:**
- All operations meet performance targets
- Performance consistent under load
- Database queries optimized

**Implementation:**
- Create performance test suite
- Use pytest-benchmark or similar
- Test with realistic data volumes

---

## Phase 3: Deployment Preparation

### Environment Configuration

**Required Environment Variables:**

**Backend (.env):**
```
DATABASE_URL=<Neon PostgreSQL connection string>
BETTER_AUTH_SECRET=<same as Feature 1>
JWT_EXPIRATION_HOURS=1
```

**Note:** All environment variables are shared with Feature 1. No new configuration needed.

### Deployment Checklist

- [ ] Database migrations applied to production
- [ ] Feature 1 (Authentication) deployed and operational
- [ ] Task API endpoints responding
- [ ] User isolation verified in production
- [ ] Error handling tested
- [ ] Performance targets met
- [ ] Logging configured
- [ ] Monitoring alerts set up

---

## Success Criteria

The Backend Task Management API feature is complete when:

1. ✅ All 6 API endpoints implemented and functional
2. ✅ Task creation persists to database
3. ✅ Task retrieval filtered by authenticated user
4. ✅ Task updates modify correct fields
5. ✅ Task deletion removes from database
6. ✅ Completion toggle changes status
7. ✅ User isolation enforced (100% of cross-user attempts blocked)
8. ✅ All validation rules enforced
9. ✅ Error handling returns appropriate status codes
10. ✅ All integration tests passing
11. ✅ Performance targets met
12. ✅ Feature 1 integration successful
13. ✅ Database schema created and migrated
14. ✅ No manual code edits required
15. ✅ Ready for frontend integration

---

## Risk Mitigation

### Risk 1: Feature 1 Dependency
**Mitigation Implemented:**
- Verify Feature 1 is operational before starting
- Import authentication dependencies early
- Test integration continuously

### Risk 2: Database Performance
**Mitigation Implemented:**
- Index user_id column
- Index task id column
- Monitor query performance
- Test with realistic data volumes

### Risk 3: Concurrent Updates
**Mitigation Implemented:**
- Document optimistic concurrency behavior
- Ensure atomic database operations
- Test concurrent scenarios

### Risk 4: Data Integrity
**Mitigation Implemented:**
- Foreign key constraints
- Validation at multiple layers
- Comprehensive testing
- Database backups

---

## Future Enhancements

**Not in scope for initial implementation:**

1. **Pagination:** Add limit/offset parameters for task lists
2. **Sorting:** Add sort parameter (by created_at, title, etc.)
3. **Filtering:** Add filter by completion status
4. **Search:** Add text search on title/description
5. **Bulk Operations:** Create/update/delete multiple tasks
6. **Task Categories:** Add category/tag support
7. **Due Dates:** Add due_date field and reminders
8. **Priority Levels:** Add priority field
9. **Task History:** Track changes over time
10. **Soft Deletes:** Add deleted_at field for recovery

---

## Appendix

### Technology References

**FastAPI:**
- Documentation: https://fastapi.tiangolo.com/
- Routing: https://fastapi.tiangolo.com/tutorial/bigger-applications/

**SQLModel:**
- Documentation: https://sqlmodel.tiangolo.com/
- Relationships: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/

**Alembic:**
- Documentation: https://alembic.sqlalchemy.org/
- Auto-generate: https://alembic.sqlalchemy.org/en/latest/autogenerate.html

### Related Documents

- Feature Specification: `specs/2-backend-task-api/spec.md`
- Feature 1 Plan: `specs/1-auth-user-isolation/plan.md`
- Data Model: `specs/2-backend-task-api/data-model.md`
- API Contracts: `specs/2-backend-task-api/contracts/`
- Project Constitution: `.specify/memory/constitution.md`

---

**End of Implementation Plan**
