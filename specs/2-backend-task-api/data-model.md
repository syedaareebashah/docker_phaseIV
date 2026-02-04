# Data Model: Backend Task Management API

**Feature ID:** 2-backend-task-api
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This document defines the data entities, relationships, and validation rules for the Backend Task Management API. The data model supports user-scoped task management with strict ownership enforcement.

---

## Entities

### Task

**Description:** Represents a user's todo item with title, description, and completion status.

**Table Name:** `tasks`

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL, DEFAULT uuid_generate_v4() | Unique identifier for the task |
| user_id | UUID | FOREIGN KEY (users.user_id), NOT NULL, INDEX | Owner of the task (references User) |
| title | VARCHAR(255) | NOT NULL | Task title (required) |
| description | TEXT | NULL | Task description (optional) |
| completed | BOOLEAN | NOT NULL, DEFAULT false | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Last modification timestamp |

**Indexes:**
- PRIMARY KEY on id
- INDEX on user_id (for fast filtering by owner)
- INDEX on (user_id, created_at) (for sorted user task lists)

**Validation Rules:**

**Title:**
- Required (cannot be null or empty string)
- Minimum length: 1 character
- Maximum length: 255 characters
- Whitespace-only titles rejected

**Description:**
- Optional (can be null or empty)
- Maximum length: 1000 characters
- No minimum length requirement

**Completed:**
- Boolean only (true/false)
- Defaults to false on creation
- Cannot be null

**User ID:**
- Must reference existing user in users table
- Cannot be null
- Cannot be changed after task creation (immutable)
- Foreign key constraint enforced at database level

**Timestamps:**
- created_at: Set automatically on record creation, immutable
- updated_at: Set automatically on creation, updated on any modification
- Both stored in UTC
- Both use ISO 8601 format in API responses

**Relationships:**
- Each task belongs to exactly one user (many-to-one)
- User can have many tasks (one-to-many)
- Foreign key: tasks.user_id → users.user_id
- ON DELETE CASCADE: Deleting user deletes all their tasks

**Security Constraints:**
- All queries must filter by user_id (user isolation)
- Task ownership cannot be transferred
- Cross-user access blocked at query level

---

## State Transitions

### Task Lifecycle

```
[No Task]
    |
    | POST /api/{user_id}/tasks (with title)
    v
[Task Created - Incomplete]
    |
    | PATCH /api/{user_id}/tasks/{id}/complete
    v
[Task Completed]
    |
    | PATCH /api/{user_id}/tasks/{id}/complete (toggle)
    v
[Task Incomplete]
    |
    | PUT /api/{user_id}/tasks/{id} (update fields)
    v
[Task Updated]
    |
    | DELETE /api/{user_id}/tasks/{id}
    v
[Task Deleted - Permanent]
```

**State Descriptions:**

1. **No Task:** Task does not exist
2. **Task Created - Incomplete:** Task exists with completed=false (default state)
3. **Task Completed:** Task exists with completed=true
4. **Task Incomplete:** Task exists with completed=false (after toggle)
5. **Task Updated:** Task fields modified, updated_at timestamp changed
6. **Task Deleted:** Task permanently removed from database (no recovery)

**State Transition Rules:**
- Creation always starts with completed=false
- Completion can be toggled any number of times
- Updates preserve completion status unless explicitly changed
- Deletion is permanent (no soft delete)
- All transitions require ownership verification

---

## Data Integrity Constraints

### Database Level

**Uniqueness:**
- id is primary key (automatically unique)
- No uniqueness constraint on title (users can have duplicate titles)

**Referential Integrity:**
- user_id must reference valid user in users table
- Foreign key constraint enforced
- ON DELETE CASCADE: Deleting user deletes all their tasks

**Data Type Constraints:**
- id: Must be valid UUID v4
- user_id: Must be valid UUID
- title: Must be valid VARCHAR(255)
- description: Must be valid TEXT
- completed: Must be valid BOOLEAN
- Timestamps: Must be valid TIMESTAMP values

**Not Null Constraints:**
- id, user_id, title, completed, created_at, updated_at cannot be null
- description can be null

### Application Level

**Ownership Enforcement:**
- All queries filtered by authenticated user_id
- Cross-user access blocked with 403 Forbidden
- Task creation assigns authenticated user as owner
- Task ownership cannot be changed

**Validation:**
- Title cannot be empty string or whitespace-only
- Title length validated (1-255 characters)
- Description length validated (0-1000 characters)
- Completed must be boolean

**Timestamp Management:**
- created_at set automatically, never modified
- updated_at set automatically on creation and updates
- Timestamps managed by database/ORM, not API

---

## Database Schema (SQL)

```sql
-- Create tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for fast filtering
CREATE INDEX idx_tasks_user_id ON tasks(user_id);

-- Create composite index for sorted user task lists
CREATE INDEX idx_tasks_user_created ON tasks(user_id, created_at DESC);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tasks_updated_at_trigger
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();

-- Add constraint to prevent empty titles
ALTER TABLE tasks ADD CONSTRAINT check_title_not_empty
    CHECK (LENGTH(TRIM(title)) > 0);
```

---

## SQLModel Definition (Python)

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Task(SQLModel, table=True):
    """Task model for user todo items."""

    __tablename__ = "tasks"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    user_id: UUID = Field(
        foreign_key="users.user_id",
        nullable=False,
        index=True
    )
    title: str = Field(
        max_length=255,
        nullable=False,
        min_length=1
    )
    description: Optional[str] = Field(
        default=None,
        max_length=1000
    )
    completed: bool = Field(
        default=False,
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

    # Relationship to User (optional, for ORM navigation)
    # user: Optional["User"] = Relationship(back_populates="tasks")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440000",
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for the API",
                "completed": false,
                "created_at": "2026-02-03T12:00:00Z",
                "updated_at": "2026-02-03T12:00:00Z"
            }
        }

class TaskCreate(SQLModel):
    """Task creation model (API request)."""

    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)

class TaskUpdate(SQLModel):
    """Task update model (API request)."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: Optional[bool] = Field(default=None)

class TaskPublic(SQLModel):
    """Public task model (API response)."""

    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

---

## Data Access Patterns

### Create Task
```python
# Validate input
if not title or not title.strip():
    raise HTTPException(status_code=400, detail="Title cannot be empty")

# Create task
task = Task(
    user_id=current_user.user_id,
    title=title.strip(),
    description=description
)

# Insert into database
session.add(task)
session.commit()
session.refresh(task)

return TaskPublic.from_orm(task)
```

### List User's Tasks
```python
# Query tasks filtered by authenticated user
tasks = session.query(Task).filter(
    Task.user_id == current_user.user_id
).order_by(Task.created_at.desc()).all()

return [TaskPublic.from_orm(task) for task in tasks]
```

### Get Single Task
```python
# Look up task by ID
task = session.get(Task, task_id)

# Verify exists
if not task:
    raise HTTPException(status_code=404, detail="Task not found")

# Verify ownership
if task.user_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="Access forbidden")

return TaskPublic.from_orm(task)
```

### Update Task
```python
# Look up task
task = session.get(Task, task_id)

# Verify exists and ownership
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
if task.user_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="Access forbidden")

# Update fields
if title is not None:
    task.title = title.strip()
if description is not None:
    task.description = description
if completed is not None:
    task.completed = completed

# updated_at handled by database trigger
session.commit()
session.refresh(task)

return TaskPublic.from_orm(task)
```

### Delete Task
```python
# Look up task
task = session.get(Task, task_id)

# Verify exists and ownership
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
if task.user_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="Access forbidden")

# Delete task
session.delete(task)
session.commit()

return {"message": "Task deleted"}
```

### Toggle Completion
```python
# Look up task
task = session.get(Task, task_id)

# Verify exists and ownership
if not task:
    raise HTTPException(status_code=404, detail="Task not found")
if task.user_id != current_user.user_id:
    raise HTTPException(status_code=403, detail="Access forbidden")

# Toggle completion
task.completed = not task.completed

# updated_at handled by database trigger
session.commit()
session.refresh(task)

return TaskPublic.from_orm(task)
```

---

## Migration Strategy

### Initial Migration (Alembic)

**File:** `alembic/versions/002_create_tasks_table.py`

```python
"""Create tasks table

Revision ID: 002
Revises: 001
Create Date: 2026-02-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '002'
down_revision = '001'  # Depends on users table from Feature 1
branch_labels = None
depends_on = None

def upgrade():
    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text('uuid_generate_v4()')),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('completed', sa.Boolean, nullable=False,
                  server_default=sa.text('false')),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False,
                  server_default=sa.text('CURRENT_TIMESTAMP'))
    )

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_tasks_user_id',
        'tasks', 'users',
        ['user_id'], ['user_id'],
        ondelete='CASCADE'
    )

    # Create indexes
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('idx_tasks_user_created', 'tasks',
                    ['user_id', sa.text('created_at DESC')])

    # Create updated_at trigger
    op.execute("""
        CREATE OR REPLACE FUNCTION update_tasks_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    op.execute("""
        CREATE TRIGGER update_tasks_updated_at_trigger
            BEFORE UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION update_tasks_updated_at();
    """)

    # Add constraint for non-empty titles
    op.execute("""
        ALTER TABLE tasks ADD CONSTRAINT check_title_not_empty
            CHECK (LENGTH(TRIM(title)) > 0);
    """)

def downgrade():
    op.drop_table('tasks')
    op.execute('DROP FUNCTION IF EXISTS update_tasks_updated_at() CASCADE')
```

---

## Testing Data

### Test Tasks

**Valid Test Task:**
```json
{
  "title": "Test task",
  "description": "This is a test task"
}
```

**Expected Result:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "Test task",
  "description": "This is a test task",
  "completed": false,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

**Test Scenarios:**
1. Create task with valid data → Success
2. Create task with empty title → 400 Bad Request
3. Create task with title > 255 chars → 400 Bad Request
4. Create task with description > 1000 chars → 400 Bad Request
5. Update task with valid data → Success
6. Update non-existent task → 404 Not Found
7. Update another user's task → 403 Forbidden
8. Delete task → Success
9. Delete non-existent task → 404 Not Found
10. Delete another user's task → 403 Forbidden
11. Toggle completion → Success
12. List tasks → Returns only user's tasks

---

**End of Data Model**
