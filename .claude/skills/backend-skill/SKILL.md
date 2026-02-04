---
name: backend-skill
description: Generate FastAPI routes, handle requests/responses, connect to database. Use for API development.
---

# Backend Skill – Generate routes, handle requests/responses, connect to DB

## Instructions

1. **Route Generation**
   - Create RESTful API endpoints using FastAPI decorators
   - Implement proper HTTP methods (GET, POST, PUT, DELETE)
   - Define clear route paths following REST conventions
   - Group related endpoints logically

2. **Request/Response Handling**
   - Use Pydantic models for request validation
   - Define response models for type safety
   - Handle query parameters and path parameters
   - Implement proper status codes (200, 201, 400, 401, 404, 500)
   - Add error handling with try-catch blocks
   - Return structured JSON responses

3. **Database Connection**
   - Configure SQLModel engine with Neon PostgreSQL
   - Create database session dependencies
   - Implement connection pooling
   - Handle database transactions properly
   - Use async operations where applicable
   - Close connections after use

4. **Authentication Integration**
   - Extract JWT tokens from Authorization headers
   - Verify token signatures using middleware
   - Decode user ID from validated tokens
   - Filter database queries by authenticated user

## Best Practices

- Use dependency injection for database sessions
- Implement request validation at the route level
- Always filter data by user_id for multi-user apps
- Return appropriate HTTP status codes
- Add comprehensive error handling
- Log requests and errors for debugging
- Use async/await for database operations
- Keep route handlers thin, delegate to service layer
- Never expose raw database errors to clients

## Example Structure
```python
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlmodel import Session, select
from typing import Annotated
import jwt

app = FastAPI()

# Database dependency
def get_session():
    with Session(engine) as session:
        yield session

# Auth dependency
def get_current_user(authorization: Annotated[str, Header()]):
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Route example
@app.get("/tasks")
async def get_tasks(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    statement = select(Task).where(Task.user_id == user_id)
    tasks = session.exec(statement).all()
    return {"tasks": tasks}

@app.post("/tasks", status_code=201)
async def create_task(
    task_data: TaskCreate,
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[str, Depends(get_current_user)]
):
    task = Task(**task_data.dict(), user_id=user_id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task
```

## Common Patterns

**Error Response Format:**
```python
{
    "detail": "Error message",
    "status_code": 400
}
```

**Success Response Format:**
```python
{
    "data": {...},
    "message": "Operation successful"
}
```

**Database Query Pattern:**
```python
# Filter by authenticated user
statement = select(Model).where(Model.user_id == user_id)
results = session.exec(statement).all()
```

## Use This Skill For

- Creating new API endpoints
- Implementing CRUD operations
- Connecting routes to database
- Handling authentication in routes
- Validating requests and responses
- Managing database sessions
- Implementing business logic in handlers