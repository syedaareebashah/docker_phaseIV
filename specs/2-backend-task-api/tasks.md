# Implementation Tasks: Backend Task Management API

**Feature ID:** 2-backend-task-api
**Version:** 1.0.0
**Status:** Ready for Implementation
**Created:** 2026-02-04
**Last Updated:** 2026-02-04

---

## Overview

This document provides a complete, dependency-ordered task list for implementing the Backend Task Management API. Tasks are organized by user story to enable independent implementation and testing of each CRUD operation.

**Total Tasks:** 78
**User Stories:** 6
**Estimated Complexity:** Medium
**Dependencies:** Feature 1 (Authentication & User Isolation) must be operational

---

## Implementation Strategy

### MVP Scope
**Minimum Viable Product includes User Stories 1-2:**
- US1: Create New Task
- US2: View All Personal Tasks

This provides basic task creation and retrieval capability.

### Incremental Delivery
After MVP, implement remaining user stories in priority order:
- US3: View Single Task
- US4: Update Task
- US5: Toggle Task Completion
- US6: Delete Task

### Parallel Execution Opportunities
Tasks marked with [P] can be executed in parallel with other [P] tasks in the same phase, as they operate on different files with no dependencies.

---

## Phase 1: Database Schema & Models

**Objective:** Establish Task data model and database schema with foreign key to User

**Independent Test Criteria:**
- [ ] Task SQLModel defined with all required fields
- [ ] Foreign key relationship to User table configured
- [ ] Alembic migration generated and reviewed
- [ ] Migration applied successfully to database
- [ ] tasks table exists with correct schema
- [ ] Foreign key constraint active and enforced
- [ ] Indexes created on user_id and (user_id, created_at)
- [ ] Can insert test task record with valid user_id

### Setup Tasks

- [ ] T001 Create backend/app/models/task.py with Task SQLModel class including id (UUID, PK), user_id (UUID, FK), title (str, max 255), description (optional str, max 1000), completed (bool, default false), created_at, and updated_at fields
- [ ] T002 Configure foreign key in Task model with Field(foreign_key="users.user_id", nullable=False, index=True) for user_id field
- [ ] T003 Add validation to Task model with Field(min_length=1, max_length=255) for title to prevent empty strings
- [ ] T004 Create TaskCreate Pydantic model in backend/app/schemas/task.py with title (required, 1-255 chars) and description (optional, max 1000 chars) fields
- [ ] T005 Create TaskUpdate Pydantic model in backend/app/schemas/task.py with title, description, and completed as Optional fields for partial updates
- [ ] T006 Create TaskPublic Pydantic model in backend/app/schemas/task.py with all Task fields for API responses
- [ ] T007 Update backend/app/models/__init__.py to export Task model for Alembic discovery
- [ ] T008 Generate Alembic migration with alembic revision --autogenerate -m "Create tasks table"
- [ ] T009 Review generated migration in backend/alembic/versions/ to ensure foreign key with ON DELETE CASCADE, indexes on user_id and (user_id, created_at DESC), and updated_at trigger are included
- [ ] T010 Add check constraint to migration for non-empty titles with ALTER TABLE tasks ADD CONSTRAINT check_title_not_empty CHECK (LENGTH(TRIM(title)) > 0)
- [ ] T011 Apply migration to database with alembic upgrade head command
- [ ] T012 Verify tasks table exists in database with correct schema, foreign key constraint, and indexes using psql or database client
- [ ] T013 Test foreign key constraint by attempting to insert task with non-existent user_id and verifying it fails
- [ ] T014 Test CASCADE delete by creating test user with tasks, deleting user, and verifying tasks are also deleted

---

## Phase 2: Authentication Integration & Utilities

**Objective:** Import Feature 1 authentication dependencies and create task-specific utilities

**Independent Test Criteria:**
- [ ] get_current_user dependency imported successfully
- [ ] User model imported successfully
- [ ] Database session dependency imported successfully
- [ ] User ID validation utility created and tested
- [ ] Task ownership verification utility created and tested
- [ ] No import errors when starting application

### Foundational Tasks

- [ ] T015 Import get_current_user dependency from backend/app/auth/dependencies.py into task routes module
- [ ] T016 Import User model from backend/app/models/user.py for type annotations
- [ ] T017 Import get_session dependency from backend/app/database.py for database access
- [ ] T018 Create backend/app/utils/validation.py with validate_user_access(route_user_id: UUID, current_user: User) function that raises HTTPException 403 if IDs don't match
- [ ] T019 Create backend/app/utils/task_helpers.py with get_task_or_404(task_id: UUID, user_id: UUID, session: Session) -> Task function that queries task with ownership verification
- [ ] T020 Implement get_task_or_404 to return 404 if task not found or not owned by user (don't reveal existence of other users' tasks)
- [ ] T021 Test validate_user_access function with matching and mismatching user IDs to verify 403 error is raised correctly
- [ ] T022 Test get_task_or_404 function with valid task, non-existent task, and other user's task to verify correct error responses

---

## Phase 3: User Story 1 - Create New Task

**Objective:** Enable authenticated users to create new tasks

**User Story:** As an authenticated user, I want to create a new task with title and optional description so that I can track things I need to do.

**Priority:** P1 (Critical - foundational CRUD operation)

**Independent Test Criteria:**
- [ ] POST /api/{user_id}/tasks endpoint accepts title and description in request body
- [ ] Endpoint validates user_id matches authenticated user (403 if mismatch)
- [ ] Title validation rejects empty strings with 400 Bad Request
- [ ] Title validation rejects strings > 255 chars with 400 Bad Request
- [ ] Description validation rejects strings > 1000 chars with 400 Bad Request
- [ ] Task created with authenticated user as owner (ignores any user_id in body)
- [ ] Task defaults to completed=false
- [ ] Timestamps (created_at, updated_at) set automatically
- [ ] Returns 201 Created with task object including generated ID
- [ ] Created task persists to database and is retrievable

### US1 Tasks

- [ ] T023 [US1] Create backend/app/routes/tasks.py with FastAPI APIRouter and /api prefix
- [ ] T024 [US1] Implement POST /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py accepting user_id path parameter and TaskCreate request body
- [ ] T025 [US1] Add get_current_user dependency to create task endpoint for authentication
- [ ] T026 [US1] Add get_session dependency to create task endpoint for database access
- [ ] T027 [US1] Validate route user_id matches authenticated user in create endpoint using validate_user_access utility
- [ ] T028 [US1] Validate title is non-empty and within length limits in create endpoint (Pydantic handles this automatically)
- [ ] T029 [US1] Create Task instance in create endpoint with user_id from current_user (not from request body), title and description from request
- [ ] T030 [US1] Set completed=false explicitly in create endpoint (or rely on model default)
- [ ] T031 [US1] Add task to session, commit, and refresh in create endpoint to get generated ID and timestamps
- [ ] T032 [US1] Return TaskPublic response with 201 Created status in create endpoint
- [ ] T033 [US1] Add error handling in create endpoint for validation errors (400), authentication errors (401), and authorization errors (403)
- [ ] T034 [US1] Register tasks router in backend/app/main.py with app.include_router(tasks_router)
- [ ] T035 [US1] Create backend/tests/test_task_create.py with integration tests for create endpoint
- [ ] T036 [US1] Test create with valid data returns 201 and task object with generated ID
- [ ] T037 [US1] Test create with empty title returns 400 validation error
- [ ] T038 [US1] Test create with title > 255 chars returns 400 validation error
- [ ] T039 [US1] Test create with description > 1000 chars returns 400 validation error
- [ ] T040 [US1] Test create with mismatched user_id returns 403 Forbidden
- [ ] T041 [US1] Test create without authentication returns 401 Unauthorized
- [ ] T042 [US1] Test created task persists to database and can be queried

---

## Phase 4: User Story 2 - View All Personal Tasks

**Objective:** Enable authenticated users to retrieve all their tasks

**User Story:** As an authenticated user, I want to see all my tasks so that I can review what needs to be done.

**Priority:** P1 (Critical - foundational CRUD operation)

**Independent Test Criteria:**
- [ ] GET /api/{user_id}/tasks endpoint returns list of tasks
- [ ] Endpoint validates user_id matches authenticated user (403 if mismatch)
- [ ] Returns only tasks owned by authenticated user (user isolation)
- [ ] Returns empty list if user has no tasks
- [ ] Tasks ordered by created_at descending (newest first)
- [ ] All task fields included in response
- [ ] Other users' tasks never included in response

### US2 Tasks

- [ ] T043 [US2] Implement GET /api/{user_id}/tasks endpoint in backend/app/routes/tasks.py accepting user_id path parameter
- [ ] T044 [US2] Add get_current_user and get_session dependencies to list tasks endpoint
- [ ] T045 [US2] Validate route user_id matches authenticated user in list endpoint using validate_user_access utility
- [ ] T046 [US2] Query tasks filtered by user_id in list endpoint with session.query(Task).filter(Task.user_id == current_user.user_id)
- [ ] T047 [US2] Order tasks by created_at descending in list endpoint with .order_by(Task.created_at.desc())
- [ ] T048 [US2] Return list of TaskPublic objects with 200 OK status in list endpoint (empty list if no tasks)
- [ ] T049 [US2] Add error handling in list endpoint for authentication errors (401) and authorization errors (403)
- [ ] T050 [US2] Create backend/tests/test_task_list.py with integration tests for list endpoint
- [ ] T051 [US2] Test list returns empty array for user with no tasks
- [ ] T052 [US2] Test list returns user's tasks in correct order (newest first)
- [ ] T053 [US2] Test list with multiple tasks returns all user's tasks
- [ ] T054 [US2] Test list does not include other users' tasks (user isolation)
- [ ] T055 [US2] Test list with mismatched user_id returns 403 Forbidden
- [ ] T056 [US2] Test list without authentication returns 401 Unauthorized

---

## Phase 5: User Story 3 - View Single Task

**Objective:** Enable authenticated users to retrieve a specific task by ID

**User Story:** As an authenticated user, I want to view details of a specific task so that I can see its full information.

**Priority:** P2 (High - supports task detail views)

**Independent Test Criteria:**
- [ ] GET /api/{user_id}/tasks/{task_id} endpoint returns single task
- [ ] Endpoint validates user_id matches authenticated user (403 if mismatch)
- [ ] Returns task if it exists and belongs to authenticated user
- [ ] Returns 404 Not Found if task doesn't exist
- [ ] Returns 404 Not Found if task belongs to different user (don't reveal existence)
- [ ] All task fields included in response

### US3 Tasks

- [ ] T057 [US3] Implement GET /api/{user_id}/tasks/{task_id} endpoint in backend/app/routes/tasks.py accepting user_id and task_id path parameters
- [ ] T058 [US3] Add get_current_user and get_session dependencies to get task endpoint
- [ ] T059 [US3] Validate route user_id matches authenticated user in get endpoint using validate_user_access utility
- [ ] T060 [US3] Look up task using get_task_or_404 utility in get endpoint to verify ownership and existence
- [ ] T061 [US3] Return TaskPublic object with 200 OK status in get endpoint
- [ ] T062 [US3] Add error handling in get endpoint for not found (404), authentication (401), and authorization (403) errors
- [ ] T063 [US3] Create backend/tests/test_task_get.py with integration tests for get endpoint
- [ ] T064 [US3] Test get returns task details for owned task
- [ ] T065 [US3] Test get returns 404 for non-existent task
- [ ] T066 [US3] Test get returns 404 for other user's task (not 403, to avoid revealing existence)
- [ ] T067 [US3] Test get with mismatched user_id returns 403 Forbidden
- [ ] T068 [US3] Test get without authentication returns 401 Unauthorized

---

## Phase 6: User Story 4 - Update Task

**Objective:** Enable authenticated users to modify their tasks

**User Story:** As an authenticated user, I want to update my task's title, description, or completion status so that I can keep my tasks current.

**Priority:** P2 (High - core CRUD operation)

**Independent Test Criteria:**
- [ ] PUT /api/{user_id}/tasks/{task_id} endpoint accepts TaskUpdate body
- [ ] Endpoint validates user_id matches authenticated user (403 if mismatch)
- [ ] Updates only provided fields (partial update support)
- [ ] Omitted fields remain unchanged
- [ ] updated_at timestamp automatically updated by database trigger
- [ ] Returns updated task with 200 OK
- [ ] Returns 404 if task doesn't exist
- [ ] Returns 404 if task belongs to different user
- [ ] Validation errors return 400 Bad Request

### US4 Tasks

- [ ] T069 [US4] Implement PUT /api/{user_id}/tasks/{task_id} endpoint in backend/app/routes/tasks.py accepting user_id, task_id path parameters and TaskUpdate request body
- [ ] T070 [US4] Add get_current_user and get_session dependencies to update task endpoint
- [ ] T071 [US4] Validate route user_id matches authenticated user in update endpoint using validate_user_access utility
- [ ] T072 [US4] Look up task using get_task_or_404 utility in update endpoint to verify ownership and existence
- [ ] T073 [US4] Update task fields in update endpoint only if provided in request body (if update_data.title is not None: task.title = update_data.title)
- [ ] T074 [US4] Commit changes and refresh task in update endpoint to get updated timestamp from database trigger
- [ ] T075 [US4] Return TaskPublic object with 200 OK status in update endpoint
- [ ] T076 [US4] Add error handling in update endpoint for validation (400), not found (404), authentication (401), and authorization (403) errors
- [ ] T077 [US4] Create backend/tests/test_task_update.py with integration tests for update endpoint
- [ ] T078 [US4] Test update with all fields updates task correctly
- [ ] T079 [US4] Test update with only title updates title and leaves other fields unchanged
- [ ] T080 [US4] Test update with only description updates description and leaves other fields unchanged
- [ ] T081 [US4] Test update with only completed updates completion status and leaves other fields unchanged
- [ ] T082 [US4] Test update with empty title returns 400 validation error
- [ ] T083 [US4] Test update with title > 255 chars returns 400 validation error
- [ ] T084 [US4] Test update of non-existent task returns 404 Not Found
- [ ] T085 [US4] Test update of other user's task returns 404 Not Found
- [ ] T086 [US4] Test update with mismatched user_id returns 403 Forbidden
- [ ] T087 [US4] Test update without authentication returns 401 Unauthorized
- [ ] T088 [US4] Verify updated_at timestamp changes after update

---

## Phase 7: User Story 5 - Toggle Task Completion

**Objective:** Enable authenticated users to mark tasks as complete or incomplete

**User Story:** As an authenticated user, I want to toggle my task's completion status so that I can track my progress.

**Priority:** P2 (High - common operation)

**Independent Test Criteria:**
- [ ] PATCH /api/{user_id}/tasks/{task_id}/complete endpoint toggles completion
- [ ] Endpoint validates user_id matches authenticated user (403 if mismatch)
- [ ] Toggles completed field (false → true, true → false)
- [ ] updated_at timestamp automatically updated by database trigger
- [ ] Returns updated task with 200 OK
- [ ] Returns 404 if task doesn't exist
- [ ] Returns 404 if task belongs to different user

### US5 Tasks

- [ ] T089 [US5] Implement PATCH /api/{user_id}/tasks/{task_id}/complete endpoint in backend/app/routes/tasks.py accepting user_id and task_id path parameters
- [ ] T090 [US5] Add get_current_user and get_session dependencies to toggle completion endpoint
- [ ] T091 [US5] Validate route user_id matches authenticated user in toggle endpoint using validate_user_access utility
- [ ] T092 [US5] Look up task using get_task_or_404 utility in toggle endpoint to verify ownership and existence
- [ ] T093 [US5] Toggle completion status in toggle endpoint with task.completed = not task.completed
- [ ] T094 [US5] Commit changes and refresh task in toggle endpoint to get updated timestamp from database trigger
- [ ] T095 [US5] Return TaskPublic object with 200 OK status in toggle endpoint
- [ ] T096 [US5] Add error handling in toggle endpoint for not found (404), authentication (401), and authorization (403) errors
- [ ] T097 [US5] Create backend/tests/test_task_toggle.py with integration tests for toggle endpoint
- [ ] T098 [US5] Test toggle changes completed from false to true
- [ ] T099 [US5] Test toggle changes completed from true to false
- [ ] T100 [US5] Test toggle of non-existent task returns 404 Not Found
- [ ] T101 [US5] Test toggle of other user's task returns 404 Not Found
- [ ] T102 [US5] Test toggle with mismatched user_id returns 403 Forbidden
- [ ] T103 [US5] Test toggle without authentication returns 401 Unauthorized
- [ ] T104 [US5] Verify updated_at timestamp changes after toggle

---

## Phase 8: User Story 6 - Delete Task

**Objective:** Enable authenticated users to permanently remove tasks

**User Story:** As an authenticated user, I want to delete tasks so that I can remove completed or unwanted items from my list.

**Priority:** P2 (High - core CRUD operation)

**Independent Test Criteria:**
- [ ] DELETE /api/{user_id}/tasks/{task_id} endpoint deletes task
- [ ] Endpoint validates user_id matches authenticated user (403 if mismatch)
- [ ] Task permanently removed from database
- [ ] Returns 204 No Content on success
- [ ] Returns 404 if task doesn't exist
- [ ] Returns 404 if task belongs to different user
- [ ] Deleted task no longer appears in list endpoint
- [ ] Subsequent requests for deleted task return 404

### US6 Tasks

- [ ] T105 [US6] Implement DELETE /api/{user_id}/tasks/{task_id} endpoint in backend/app/routes/tasks.py accepting user_id and task_id path parameters
- [ ] T106 [US6] Add get_current_user and get_session dependencies to delete task endpoint
- [ ] T107 [US6] Validate route user_id matches authenticated user in delete endpoint using validate_user_access utility
- [ ] T108 [US6] Look up task using get_task_or_404 utility in delete endpoint to verify ownership and existence
- [ ] T109 [US6] Delete task from database in delete endpoint with session.delete(task) and session.commit()
- [ ] T110 [US6] Return 204 No Content status in delete endpoint (no response body)
- [ ] T111 [US6] Add error handling in delete endpoint for not found (404), authentication (401), and authorization (403) errors
- [ ] T112 [US6] Create backend/tests/test_task_delete.py with integration tests for delete endpoint
- [ ] T113 [US6] Test delete removes task from database
- [ ] T114 [US6] Test delete returns 204 No Content
- [ ] T115 [US6] Test deleted task no longer appears in list endpoint
- [ ] T116 [US6] Test subsequent get request for deleted task returns 404 Not Found
- [ ] T117 [US6] Test delete of non-existent task returns 404 Not Found
- [ ] T118 [US6] Test delete of other user's task returns 404 Not Found
- [ ] T119 [US6] Test delete with mismatched user_id returns 403 Forbidden
- [ ] T120 [US6] Test delete without authentication returns 401 Unauthorized

---

## Phase 9: Integration Testing & Validation

**Objective:** Verify complete task API works correctly with user isolation

**Independent Test Criteria:**
- [ ] Complete CRUD workflow succeeds (create → list → get → update → toggle → delete)
- [ ] User isolation enforced across all operations
- [ ] Concurrent operations handled correctly
- [ ] Performance targets met for all operations
- [ ] Error handling consistent across all endpoints
- [ ] Integration with Feature 1 authentication verified

### Validation Tasks

- [ ] T121 Create backend/tests/test_task_integration.py with end-to-end workflow tests
- [ ] T122 Test complete CRUD workflow: create task → verify in list → get task → update task → toggle completion → delete task → verify not in list
- [ ] T123 Test user isolation: create two users, have each create tasks, verify neither can access the other's tasks via list, get, update, toggle, or delete
- [ ] T124 Test concurrent task creation by same user succeeds without conflicts
- [ ] T125 Test concurrent updates to same task (last update wins, optimistic concurrency)
- [ ] T126 Measure task creation performance and verify < 200ms target
- [ ] T127 Measure task list retrieval performance with 100 tasks and verify < 500ms target
- [ ] T128 Measure single task retrieval performance and verify < 100ms target
- [ ] T129 Measure task update performance and verify < 200ms target
- [ ] T130 Measure task deletion performance and verify < 200ms target
- [ ] T131 Test all error scenarios return correct HTTP status codes (400, 401, 403, 404)
- [ ] T132 Test error responses have consistent format with "detail" field
- [ ] T133 Verify Feature 1 authentication integration: valid token succeeds, invalid token fails, expired token fails
- [ ] T134 Test CASCADE delete: delete user and verify all their tasks are also deleted
- [ ] T135 Run all tests with pytest and verify 100% pass rate

---

## Dependencies & Execution Order

### User Story Dependencies

```
Setup (Phase 1)
    ↓
Foundational (Phase 2)
    ↓
    ├─→ US1: Create Task (Phase 3) ← P1 Critical
    ├─→ US2: List Tasks (Phase 4) ← P1 Critical
    │   (Can run in parallel)
    │
    └─→ US3: Get Task (Phase 5) ← P2 High (depends on US1)
            ↓
            ├─→ US4: Update Task (Phase 6) ← P2 High
            ├─→ US5: Toggle Completion (Phase 7) ← P2 High
            └─→ US6: Delete Task (Phase 8) ← P2 High
                (Can run in parallel)
                    ↓
                    └─→ Integration Testing (Phase 9) ← Final validation
```

### Critical Path
1. **Phase 1 (Setup)** → MUST complete first - establishes database schema
2. **Phase 2 (Foundational)** → MUST complete before user stories - provides utilities
3. **Phases 3-4 (US1-US2)** → Can be done in parallel - create and list operations
4. **Phase 5 (US3)** → Depends on US1 - needs tasks to retrieve
5. **Phases 6-8 (US4-US6)** → Can be done in parallel after Phase 5 - all modify operations
6. **Phase 9 (Testing)** → MUST complete last - validates entire system

### Parallel Execution Examples

**Phase 3-4 Parallel Execution:**
```bash
# After Phase 2 completes, can execute in parallel:
Phase 3 (US1: Create Task) + Phase 4 (US2: List Tasks)
```

**Phase 6-8 Parallel Execution:**
```bash
# After Phase 5 completes, can execute in parallel:
Phase 6 (US4: Update) + Phase 7 (US5: Toggle) + Phase 8 (US6: Delete)
```

---

## Task Summary by Phase

| Phase | User Story | Task Count | Parallelizable | Priority |
|-------|------------|------------|----------------|----------|
| 1 | Setup & Database | 14 | 0 | - |
| 2 | Foundational | 8 | 0 | - |
| 3 | US1: Create Task | 20 | 0 | P1 |
| 4 | US2: List Tasks | 14 | 0 | P1 |
| 5 | US3: Get Task | 12 | 0 | P2 |
| 6 | US4: Update Task | 20 | 0 | P2 |
| 7 | US5: Toggle Completion | 16 | 0 | P2 |
| 8 | US6: Delete Task | 16 | 0 | P2 |
| 9 | Integration Testing | 15 | 0 | - |
| **Total** | **6 User Stories** | **135** | **0** | - |

---

## Validation Checklist

Before marking feature as complete, verify:

- [ ] All 135 tasks completed and checked off
- [ ] All 6 user stories independently tested and passing
- [ ] Task creation persists to database
- [ ] Task list filtered by authenticated user only
- [ ] Single task retrieval verifies ownership
- [ ] Task updates modify correct fields
- [ ] Completion toggle changes status
- [ ] Task deletion removes from database
- [ ] User isolation enforced (100% of cross-user attempts blocked)
- [ ] All validation rules enforced (title required, length limits)
- [ ] Error handling returns appropriate status codes
- [ ] All integration tests passing
- [ ] Performance targets met (create < 200ms, list < 500ms, get < 100ms)
- [ ] Feature 1 integration successful
- [ ] Database schema created with foreign keys and indexes
- [ ] CASCADE delete works correctly
- [ ] All acceptance criteria from spec.md satisfied

---

## Notes

**Task Format:**
- All tasks follow format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- [P] indicates task can be parallelized (none in this feature due to sequential dependencies)
- [US#] indicates which user story the task belongs to (US1-US6)
- Task IDs are sequential (T001-T135) in execution order

**File Paths:**
- Backend files relative to backend/ directory
- Use exact paths specified in tasks for consistency

**Testing:**
- Each phase includes independent test criteria
- Test criteria must pass before moving to next phase
- Final validation checklist ensures feature completeness

**Dependencies:**
- Feature 1 (Authentication & User Isolation) MUST be operational
- All authentication dependencies imported from Feature 1
- Database connection shared with Feature 1

**User Story Mapping:**
- US1: Create New Task → Scenario 1 from spec.md
- US2: View All Personal Tasks → Scenario 2 from spec.md
- US3: View Single Task → Scenario 3 from spec.md
- US4: Update Task → Scenario 4 from spec.md
- US5: Toggle Task Completion → Scenario 5 from spec.md
- US6: Delete Task → Scenario 6 from spec.md

---

**End of Implementation Tasks**
