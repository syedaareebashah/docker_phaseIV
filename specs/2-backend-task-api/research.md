# Research Findings: Backend Task Management API

**Feature ID:** 2-backend-task-api
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This document consolidates research findings for technical decisions made during the planning phase of the Backend Task Management API. Each decision includes rationale, alternatives considered, and implementation guidance.

**Note:** Most backend infrastructure decisions were made in Feature 1 (Authentication & User Isolation). This document focuses on task-specific decisions.

---

## R1: SQLModel Relationships and Foreign Keys

### Decision
Define foreign key relationship from Task to User using SQLModel's Field with foreign_key parameter, with CASCADE delete behavior.

### Rationale
- **Data Integrity:** Foreign key ensures task always references valid user
- **Cascade Delete:** Automatically removes user's tasks when user is deleted
- **Query Optimization:** Foreign key enables database-level join optimization
- **Type Safety:** SQLModel provides typed relationship navigation

### Alternatives Considered

**1. No Foreign Key (Application-Level Only)**
- Pros: More flexible, no database constraint
- Cons: Risk of orphaned tasks, no referential integrity guarantee
- Verdict: Rejected - Database-level integrity is critical

**2. Soft Delete for Users**
- Pros: Preserves task history when user deleted
- Cons: Complexity, violates Feature 1 design, data retention issues
- Verdict: Rejected - Not in scope, CASCADE delete is simpler

**3. Manual Cascade (Application Code)**
- Pros: More control over deletion process
- Cons: Error-prone, can miss edge cases, not atomic
- Verdict: Rejected - Database CASCADE is more reliable

### Implementation Guidance

**SQLModel Foreign Key Definition:**
```python
from sqlmodel import SQLModel, Field
from uuid import UUID

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(
        foreign_key="users.user_id",  # References users table
        nullable=False,
        index=True  # Index for fast filtering
    )
    # ... other fields
```

**Alembic Migration:**
```python
# Create foreign key with CASCADE delete
op.create_foreign_key(
    'fk_tasks_user_id',
    'tasks', 'users',
    ['user_id'], ['user_id'],
    ondelete='CASCADE'  # Delete tasks when user deleted
)
```

**Index Creation:**
```python
# Index on user_id for fast filtering
op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])

# Composite index for sorted user task lists
op.create_index(
    'idx_tasks_user_created',
    'tasks',
    ['user_id', sa.text('created_at DESC')]
)
```

### References
- SQLModel Relationships: https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/
- PostgreSQL Foreign Keys: https://www.postgresql.org/docs/current/ddl-constraints.html#DDL-CONSTRAINTS-FK

---

## R2: RESTful Route Design for Nested Resources

### Decision
Use nested route pattern `/api/{user_id}/tasks` with explicit user_id in path, validated against authenticated user.

### Rationale
- **RESTful Convention:** Standard pattern for user-scoped resources
- **Explicit Ownership:** User ID visible in URL makes ownership clear
- **Validation Point:** Provides explicit point to verify user_id matches authenticated user
- **API Clarity:** Self-documenting URLs show resource hierarchy

### Alternatives Considered

**1. Flat Routes (/api/tasks)**
- Pros: Simpler URLs, no user_id validation needed
- Cons: Less RESTful, ownership not explicit in URL
- Verdict: Rejected - Nested routes are more RESTful and explicit

**2. Query Parameter (/api/tasks?user_id=...)**
- Pros: Flexible, optional filtering
- Cons: Not RESTful, query params for required filters is anti-pattern
- Verdict: Rejected - Path parameters are correct for required identifiers

**3. Subdomain (user123.api.example.com/tasks)**
- Pros: Complete isolation, scalable
- Cons: Overkill for this application, complex routing
- Verdict: Rejected - Too complex for current requirements

### Implementation Guidance

**Route Definition (FastAPI):**
```python
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

router = APIRouter(prefix="/api")

@router.get("/{user_id}/tasks")
async def list_tasks(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """List all tasks for authenticated user."""

    # Validate user_id matches authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )

    # Query tasks filtered by user_id
    tasks = session.query(Task).filter(
        Task.user_id == current_user.user_id
    ).all()

    return tasks
```

**Validation Utility:**
```python
def validate_user_access(
    route_user_id: UUID,
    current_user: User
) -> None:
    """
    Validate route user_id matches authenticated user.

    Raises:
        HTTPException: 403 if user_id mismatch
    """
    if route_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="Access forbidden"
        )
```

**Usage:**
```python
@router.get("/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user)
):
    # Validate user access
    validate_user_access(user_id, current_user)

    # Proceed with operation
    task = session.get(Task, task_id)
    # ...
```

### References
- RESTful API Design: https://restfulapi.net/resource-naming/
- FastAPI Path Parameters: https://fastapi.tiangolo.com/tutorial/path-params/

---

## R3: Partial Update Patterns (PATCH vs PUT)

### Decision
Use PUT for full/partial task updates (title, description, completed) and PATCH specifically for completion toggle endpoint.

### Rationale
- **PUT for Updates:** FastAPI/Pydantic makes partial updates easy with Optional fields
- **PATCH for Toggle:** Semantic clarity - PATCH indicates partial modification
- **Simplicity:** One update endpoint (PUT) handles all field updates
- **RESTful Semantics:** PATCH for specific action (toggle) is idiomatic

### Alternatives Considered

**1. PATCH for All Updates**
- Pros: More semantically correct for partial updates
- Cons: No practical difference in FastAPI, PUT is more common
- Verdict: Acceptable but PUT is simpler and more widely used

**2. Separate Endpoints for Each Field**
- Pros: Very explicit, fine-grained control
- Cons: Too many endpoints, maintenance burden
- Verdict: Rejected - Overkill for simple task model

**3. Single PATCH Endpoint (No Separate Toggle)**
- Pros: Fewer endpoints
- Cons: Less semantic clarity for common operation
- Verdict: Rejected - Toggle is common enough to warrant dedicated endpoint

### Implementation Guidance

**PUT Endpoint (General Update):**
```python
from pydantic import BaseModel
from typing import Optional

class TaskUpdate(BaseModel):
    """All fields optional for partial updates."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

@router.put("/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: UUID,
    task_id: UUID,
    update_data: TaskUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update task fields (partial update supported)."""

    # Validate and get task
    validate_user_access(user_id, current_user)
    task = get_task_or_404(task_id, current_user.user_id)

    # Update only provided fields
    if update_data.title is not None:
        task.title = update_data.title
    if update_data.description is not None:
        task.description = update_data.description
    if update_data.completed is not None:
        task.completed = update_data.completed

    # Save and return
    session.commit()
    session.refresh(task)
    return task
```

**PATCH Endpoint (Completion Toggle):**
```python
@router.patch("/{user_id}/tasks/{task_id}/complete")
async def toggle_task_completion(
    user_id: UUID,
    task_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """Toggle task completion status."""

    # Validate and get task
    validate_user_access(user_id, current_user)
    task = get_task_or_404(task_id, current_user.user_id)

    # Toggle completion
    task.completed = not task.completed

    # Save and return
    session.commit()
    session.refresh(task)
    return task
```

**Why This Works:**
- PUT with Optional fields = partial update capability
- PATCH for toggle = semantic clarity for common operation
- Both patterns are RESTful and idiomatic

### References
- HTTP Methods: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods
- REST API Best Practices: https://restfulapi.net/http-methods/

---

## R4: Query-Level User Isolation

### Decision
Filter all task queries by authenticated user_id at the database query level, in addition to route-level validation.

### Rationale
- **Defense in Depth:** Multiple layers of security
- **Fail-Safe:** Even if route validation fails, database won't return wrong data
- **Performance:** Database can use indexes for filtering
- **Simplicity:** Single WHERE clause ensures isolation

### Implementation Guidance

**Always Filter by User ID:**
```python
# List tasks - ALWAYS filter by user_id
tasks = session.query(Task).filter(
    Task.user_id == current_user.user_id
).all()

# Get single task - filter by user_id AND task_id
task = session.query(Task).filter(
    Task.id == task_id,
    Task.user_id == current_user.user_id  # Critical!
).first()

# Alternative using session.get() + ownership check
task = session.get(Task, task_id)
if task and task.user_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="Access forbidden")
```

**Helper Function:**
```python
def get_task_or_404(
    task_id: UUID,
    user_id: UUID,
    session: Session
) -> Task:
    """
    Get task by ID with ownership verification.

    Args:
        task_id: Task ID to look up
        user_id: Authenticated user ID
        session: Database session

    Returns:
        Task if found and owned by user

    Raises:
        HTTPException: 404 if not found, 403 if not owned
    """
    task = session.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()

    if not task:
        # Could be not found OR not owned - return 404 for security
        # (don't reveal existence of other users' tasks)
        raise HTTPException(status_code=404, detail="Task not found")

    return task
```

**Why This Matters:**
- Route validation can be bypassed by bugs
- Database filtering is last line of defense
- Performance benefit from indexed filtering
- Consistent isolation across all operations

### References
- Defense in Depth: https://owasp.org/www-community/Defense_in_Depth
- Database Security: https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html

---

## R5: Automatic Timestamp Management

### Decision
Use database triggers for updated_at timestamp management rather than application-level updates.

### Rationale
- **Reliability:** Database trigger always fires, can't be forgotten
- **Consistency:** Same mechanism across all tables
- **Performance:** Database-level operation is fast
- **Simplicity:** No application code needed

### Implementation Guidance

**Database Trigger (PostgreSQL):**
```sql
-- Create trigger function
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Attach trigger to tasks table
CREATE TRIGGER update_tasks_updated_at_trigger
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();
```

**SQLModel Configuration:**
```python
from datetime import datetime
from sqlmodel import Field

class Task(SQLModel, table=True):
    # created_at: set once, never changed
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    # updated_at: set on creation, updated by trigger
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
```

**Application Code:**
```python
# No need to manually update timestamp!
task.title = "New title"
session.commit()  # Trigger automatically updates updated_at
```

**Benefits:**
- Can't forget to update timestamp
- Consistent across all update operations
- Works even with bulk updates
- Database-level guarantee

### References
- PostgreSQL Triggers: https://www.postgresql.org/docs/current/sql-createtrigger.html
- SQLModel Timestamps: https://sqlmodel.tiangolo.com/tutorial/automatic-id-none-refresh/

---

## Summary

All research topics have been resolved with concrete implementation guidance. Key decisions:

1. **Foreign Key with CASCADE:** Ensures data integrity and automatic cleanup
2. **Nested Routes:** RESTful pattern with explicit user_id validation
3. **PUT + PATCH:** PUT for general updates, PATCH for toggle
4. **Query-Level Filtering:** Defense in depth for user isolation
5. **Database Triggers:** Automatic timestamp management

These decisions build on Feature 1's authentication infrastructure and provide a secure, maintainable task management API.

---

**End of Research Findings**
