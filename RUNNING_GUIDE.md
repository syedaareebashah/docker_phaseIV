# Todo Application - Quick Start Guide

## Running the Backend API Server

1. Navigate to the backend directory:
```bash
cd backend
```

2. Start the development server:
```bash
uvicorn app.main:app --reload --port 8000
```

3. The API will be available at: http://localhost:8000

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/signin` - Login to existing account
- `GET /auth/me` - Get current user info (requires auth)

### Task Management
- `POST /api/{user_id}/tasks` - Create new task
- `GET /api/{user_id}/tasks` - List user's tasks
- `GET /api/{user_id}/tasks/{task_id}` - Get specific task
- `PUT /api/{user_id}/tasks/{task_id}` - Update task
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task

## Running Tests

To run all tests:
```bash
python -m pytest tests/ -v
```

To run specific test file:
```bash
python -m pytest tests/test_auth_signup.py -v
```

## Environment Variables
The application uses the following environment variables:
- `BETTER_AUTH_SECRET` - Secret key for JWT signing (minimum 32 chars)
- `JWT_EXPIRATION_HOURS` - Token expiration time
- `DATABASE_URL` - Database connection string

## Frontend Integration
The backend is configured to accept requests from http://localhost:3000 (default Next.js port).