# Quickstart Guide: Backend Task Management API

**Feature ID:** 2-backend-task-api
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This guide provides step-by-step instructions for setting up and using the Backend Task Management API. This feature builds on Feature 1 (Authentication & User Isolation) and provides CRUD operations for user tasks.

**What You'll Learn:**
- How to set up the task database schema
- How to create and manage tasks via API
- How to enforce user isolation in task operations
- How to troubleshoot common issues

---

## Prerequisites

**Required:**
- Feature 1 (Authentication & User Isolation) fully implemented and operational
- Database migrations from Feature 1 applied
- Authentication system working (JWT tokens)
- Python 3.10+
- FastAPI installed
- SQLModel installed
- Alembic installed

**Verify Feature 1 is Working:**
```bash
# Test authentication endpoint
curl -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}'

# Should return JWT token
```

---

## Setup Instructions

### Step 1: Create Database Migration

Generate migration for tasks table:

```bash
# Backend directory
alembic revision --autogenerate -m "create_tasks_table"
```

**Verify migration file created:**
```bash
ls alembic/versions/
# Should see: 002_create_tasks_table.py
```

### Step 2: Review Migration

Open the generated migration file and verify it includes:
- tasks table creation
- Foreign key to users table
- Indexes on user_id
- Timestamp trigger
- Title validation constraint

**Expected migration content:**
```python
def upgrade():
    op.create_table('tasks', ...)
    op.create_foreign_key('fk_tasks_user_id', ...)
    op.create_index('idx_tasks_user_id', ...)
    # ... etc
```

### Step 3: Apply Migration

Apply the migration to create tasks table:

```bash
alembic upgrade head
```

**Verify table created:**
```sql
-- Connect to database
\dt tasks

-- Check table structure
\d tasks
```

**Expected output:**
```
Table "public.tasks"
   Column    |            Type             | Nullable | Default
-------------+-----------------------------+----------+---------
 id          | uuid                        | not null | uuid_generate_v4()
 user_id     | uuid                        | not null |
 title       | character varying(255)      | not null |
 description | text                        |          |
 completed   | boolean                     | not null | false
 created_at  | timestamp without time zone | not null | CURRENT_TIMESTAMP
 updated_at  | timestamp without time zone | not null | CURRENT_TIMESTAMP
```

### Step 4: Verify Foreign Key

Check foreign key constraint exists:

```sql
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_name = 'tasks' AND tc.constraint_type = 'FOREIGN KEY';
```

**Expected:** Foreign key from tasks.user_id to users.user_id

---

## Usage Guide

### Creating Tasks

**Step 1: Authenticate and get token**

```bash
# Sign in to get JWT token
TOKEN=$(curl -s -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123"}' \
  | jq -r '.token')

echo "Token: $TOKEN"
```

**Step 2: Get your user ID**

```bash
# Get current user info
USER_ID=$(curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.user_id')

echo "User ID: $USER_ID"
```

**Step 3: Create a task**

```bash
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs"
  }'
```

**Expected response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "completed": false,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:00:00Z"
}
```

### Listing Tasks

**Get all your tasks:**

```bash
curl -X GET "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "660e8400-e29b-41d4-a716-446655440000",
    "title": "Complete project documentation",
    "description": "Write comprehensive API docs",
    "completed": false,
    "created_at": "2026-02-03T12:00:00Z",
    "updated_at": "2026-02-03T12:00:00Z"
  }
]
```

**Empty list if no tasks:**
```json
[]
```

### Getting Single Task

```bash
# Save task ID from creation response
TASK_ID="550e8400-e29b-41d4-a716-446655440000"

curl -X GET "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### Updating Tasks

**Update task fields:**

```bash
curl -X PUT "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "description": "Updated description",
    "completed": true
  }'
```

**Partial update (only title):**

```bash
curl -X PUT "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New title only"
  }'
```

### Toggling Completion

**Mark task as complete (or incomplete if already complete):**

```bash
curl -X PATCH "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID/complete" \
  -H "Authorization: Bearer $TOKEN"
```

**Response shows toggled status:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "660e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project documentation",
  "description": "Write comprehensive API docs",
  "completed": true,
  "created_at": "2026-02-03T12:00:00Z",
  "updated_at": "2026-02-03T12:10:00Z"
}
```

### Deleting Tasks

**Permanently delete a task:**

```bash
curl -X DELETE "http://localhost:8000/api/$USER_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected response (204 No Content):**
```
(empty response body)
```

---

## Testing User Isolation

### Test 1: Create Two Users

```bash
# Create User 1
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"TestPass123"}'

# Create User 2
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@example.com","password":"TestPass123"}'
```

### Test 2: User 1 Creates Task

```bash
# Get User 1 token
TOKEN1=$(curl -s -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@example.com","password":"TestPass123"}' \
  | jq -r '.token')

USER1_ID=$(curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN1" \
  | jq -r '.user_id')

# Create task as User 1
TASK_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/$USER1_ID/tasks" \
  -H "Authorization: Bearer $TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{"title":"User 1 task"}')

TASK_ID=$(echo $TASK_RESPONSE | jq -r '.id')
echo "User 1 created task: $TASK_ID"
```

### Test 3: User 2 Attempts to Access User 1's Task

```bash
# Get User 2 token
TOKEN2=$(curl -s -X POST http://localhost:8000/auth/signin \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@example.com","password":"TestPass123"}' \
  | jq -r '.token')

USER2_ID=$(curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN2" \
  | jq -r '.user_id')

# Try to get User 1's task as User 2 (should fail)
curl -X GET "http://localhost:8000/api/$USER2_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN2"
```

**Expected response (404 Not Found):**
```json
{
  "detail": "Task not found"
}
```

**Note:** Returns 404 instead of 403 to avoid revealing existence of other users' tasks.

### Test 4: User 2 Lists Tasks (Should Be Empty)

```bash
curl -X GET "http://localhost:8000/api/$USER2_ID/tasks" \
  -H "Authorization: Bearer $TOKEN2"
```

**Expected response:**
```json
[]
```

**User 1's task is NOT visible to User 2!**

---

## Troubleshooting

### Issue: "Task not found" for existing task

**Symptoms:**
- Task exists in database
- GET request returns 404

**Possible Causes:**
1. Task belongs to different user
2. Wrong task ID
3. User ID mismatch in route

**Solutions:**

**1. Verify task ownership:**
```sql
SELECT id, user_id, title FROM tasks WHERE id = '<task_id>';
```

**2. Verify authenticated user:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.user_id'
```

**3. Check user_id in route matches authenticated user:**
```bash
# Route user_id should match authenticated user_id
echo "Route user_id: $USER_ID"
echo "Authenticated user_id: $(curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" | jq -r '.user_id')"
```

### Issue: "Access forbidden" (403)

**Symptoms:**
- Request returns 403 Forbidden
- Have valid authentication token

**Possible Causes:**
1. Route user_id doesn't match authenticated user_id
2. Attempting to access another user's task

**Solutions:**

**1. Verify route user_id:**
```bash
# Make sure you're using YOUR user_id in the route
USER_ID=$(curl -s -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.user_id')

# Use this user_id in all routes
curl -X GET "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN"
```

### Issue: "Title cannot be empty"

**Symptoms:**
- Task creation fails with validation error

**Possible Causes:**
1. Title field missing
2. Title is empty string
3. Title is whitespace only

**Solutions:**

**1. Ensure title is provided:**
```bash
# ❌ Wrong - no title
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description":"No title"}'

# ✅ Correct - title provided
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Valid title"}'
```

**2. Ensure title is not empty:**
```bash
# ❌ Wrong - empty title
-d '{"title":""}'

# ❌ Wrong - whitespace only
-d '{"title":"   "}'

# ✅ Correct - non-empty title
-d '{"title":"Valid title"}'
```

### Issue: Foreign key constraint violation

**Symptoms:**
- Database error when creating task
- "violates foreign key constraint"

**Possible Causes:**
1. user_id doesn't exist in users table
2. Authentication system not working

**Solutions:**

**1. Verify user exists:**
```sql
SELECT user_id, email FROM users WHERE user_id = '<user_id>';
```

**2. Verify authentication working:**
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Issue: updated_at not updating

**Symptoms:**
- Task updated but updated_at timestamp unchanged

**Possible Causes:**
1. Database trigger not created
2. Trigger not firing

**Solutions:**

**1. Verify trigger exists:**
```sql
SELECT trigger_name, event_manipulation, event_object_table
FROM information_schema.triggers
WHERE event_object_table = 'tasks';
```

**Expected:** `update_tasks_updated_at_trigger` on UPDATE

**2. Recreate trigger:**
```sql
DROP TRIGGER IF EXISTS update_tasks_updated_at_trigger ON tasks;

CREATE TRIGGER update_tasks_updated_at_trigger
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_tasks_updated_at();
```

---

## Integration with Frontend

### Frontend API Client Setup

**Example using Axios (from Feature 1):**

```typescript
import apiClient from '@/lib/api-client'

// Create task
const createTask = async (userId: string, title: string, description?: string) => {
  const response = await apiClient.post(`/api/${userId}/tasks`, {
    title,
    description
  })
  return response.data
}

// List tasks
const listTasks = async (userId: string) => {
  const response = await apiClient.get(`/api/${userId}/tasks`)
  return response.data
}

// Get single task
const getTask = async (userId: string, taskId: string) => {
  const response = await apiClient.get(`/api/${userId}/tasks/${taskId}`)
  return response.data
}

// Update task
const updateTask = async (
  userId: string,
  taskId: string,
  updates: { title?: string; description?: string; completed?: boolean }
) => {
  const response = await apiClient.put(`/api/${userId}/tasks/${taskId}`, updates)
  return response.data
}

// Delete task
const deleteTask = async (userId: string, taskId: string) => {
  await apiClient.delete(`/api/${userId}/tasks/${taskId}`)
}

// Toggle completion
const toggleTaskCompletion = async (userId: string, taskId: string) => {
  const response = await apiClient.patch(`/api/${userId}/tasks/${taskId}/complete`)
  return response.data
}
```

**Note:** API client from Feature 1 automatically attaches JWT token!

---

## Quick Reference

### Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| DATABASE_URL | Yes | `postgresql://user:pass@host:5432/db` |
| BETTER_AUTH_SECRET | Yes | (from Feature 1) |
| JWT_EXPIRATION_HOURS | Yes | `1` |

### API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/{user_id}/tasks | List all tasks |
| POST | /api/{user_id}/tasks | Create task |
| GET | /api/{user_id}/tasks/{id} | Get single task |
| PUT | /api/{user_id}/tasks/{id} | Update task |
| DELETE | /api/{user_id}/tasks/{id} | Delete task |
| PATCH | /api/{user_id}/tasks/{id}/complete | Toggle completion |

### Common Commands

```bash
# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check database
psql $DATABASE_URL -c "\dt tasks"

# Test task creation
curl -X POST "http://localhost:8000/api/$USER_ID/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test task"}'
```

---

## Next Steps

Now that the Backend Task Management API is set up, you can:

1. **Build Frontend UI** - Create React components to display and manage tasks
2. **Add Features** - Implement pagination, sorting, filtering (future enhancements)
3. **Monitor Performance** - Track API response times and optimize queries
4. **Add Tests** - Write integration tests for all endpoints

For more information, see:
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [API Contracts](./contracts/task-api.yaml)
- [Research Findings](./research.md)

---

**End of Quickstart Guide**
