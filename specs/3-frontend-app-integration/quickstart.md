# Quickstart Guide: Frontend Application & Integration

**Feature ID:** 3-frontend-app-integration
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This guide provides step-by-step instructions for setting up and running the Frontend Application & Integration feature. This completes the full-stack Todo application by providing the user-facing web interface.

**What You'll Learn:**
- How to set up the Next.js frontend project
- How to configure authentication integration
- How to connect to the backend API
- How to run and test the application
- How to troubleshoot common issues

---

## Prerequisites

**Required:**
- Node.js 18+ installed
- npm or yarn package manager
- Feature 1 (Authentication) backend running
- Feature 2 (Backend Task API) running
- Backend accessible at known URL (e.g., http://localhost:8000)

**Verify Backend is Running:**
```bash
# Test authentication endpoint
curl http://localhost:8000/auth/signin

# Test task endpoint (with token)
curl http://localhost:8000/api/{user_id}/tasks \
  -H "Authorization: Bearer <token>"
```

---

## Setup Instructions

### Step 1: Create Next.js Project

Initialize a new Next.js project with App Router:

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir
cd frontend
```

**Configuration options:**
- ✅ TypeScript
- ✅ Tailwind CSS
- ✅ App Router
- ❌ src/ directory (use app/ directly)

### Step 2: Install Dependencies

Install required packages:

```bash
npm install axios better-auth
```

**Packages:**
- `axios`: HTTP client for API requests
- `better-auth`: Authentication library

### Step 3: Configure Environment Variables

Create `.env.local` file in project root:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same secret as backend>
```

**Important:**
- `NEXT_PUBLIC_` prefix makes variable accessible in browser
- `BETTER_AUTH_SECRET` must match backend configuration

**Verify configuration:**
```bash
echo $NEXT_PUBLIC_API_URL
# Should output: http://localhost:8000
```

### Step 4: Create Project Structure

Create the directory structure:

```bash
mkdir -p app/\(auth\)/signin
mkdir -p app/\(auth\)/signup
mkdir -p app/\(app\)/tasks
mkdir -p components/auth
mkdir -p components/tasks
mkdir -p components/ui
mkdir -p lib
mkdir -p contexts
mkdir -p hooks
```

### Step 5: Start Development Server

Run the development server:

```bash
npm run dev
```

**Expected output:**
```
- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully
```

**Verify:**
- Open http://localhost:3000 in browser
- Should see Next.js default page (will be replaced)

---

## Usage Guide

### Running the Complete Application

**Step 1: Start Backend Services**

```bash
# Terminal 1: Start FastAPI backend
cd backend
uvicorn main:app --reload --port 8000
```

**Step 2: Start Frontend**

```bash
# Terminal 2: Start Next.js frontend
cd frontend
npm run dev
```

**Step 3: Access Application**

Open browser to http://localhost:3000

### User Flow Walkthrough

#### 1. Sign Up

1. Navigate to http://localhost:3000
2. Click "Sign Up" or navigate to /signup
3. Enter email and password
4. Click "Sign Up" button
5. Should redirect to /tasks

**Expected Result:**
- User account created in backend
- JWT token issued
- Redirected to task management interface
- Empty task list displayed (new user)

#### 2. Sign In

1. Navigate to http://localhost:3000/signin
2. Enter email and password
3. Click "Sign In" button
4. Should redirect to /tasks

**Expected Result:**
- User authenticated
- JWT token issued
- Redirected to task management interface
- Existing tasks displayed (if any)

#### 3. Create Task

1. On /tasks page, find "Create Task" form
2. Enter task title (required)
3. Optionally enter description
4. Click "Create" button

**Expected Result:**
- New task appears in list immediately
- Task persisted to backend
- Form clears for next task

#### 4. Edit Task

1. Click "Edit" button on a task
2. Modify title or description
3. Click "Save" button

**Expected Result:**
- Task updates in list
- Changes persisted to backend
- Returns to view mode

#### 5. Toggle Completion

1. Click checkbox or toggle on a task
2. Visual state updates immediately

**Expected Result:**
- Completion status toggles
- Change persisted to backend
- Visual indicator updates

#### 6. Delete Task

1. Click "Delete" button on a task
2. Confirm deletion in prompt
3. Task removed from list

**Expected Result:**
- Task disappears from list
- Task deleted from backend
- Cannot be recovered

#### 7. Logout

1. Click "Logout" button
2. Redirected to signin page

**Expected Result:**
- Authentication cleared
- Cannot access /tasks without signing in again
- Must sign in to continue

---

## Testing Multi-User Isolation

### Test Scenario: Two Users

**Step 1: Create First User**

```bash
# Browser 1 (or Incognito Window 1)
1. Navigate to http://localhost:3000/signup
2. Sign up as user1@example.com
3. Create some tasks
4. Note the tasks created
```

**Step 2: Create Second User**

```bash
# Browser 2 (or Incognito Window 2)
1. Navigate to http://localhost:3000/signup
2. Sign up as user2@example.com
3. Should see empty task list
4. Create different tasks
```

**Step 3: Verify Isolation**

```bash
# Browser 1 (user1@example.com)
- Should only see User 1's tasks
- Should NOT see User 2's tasks

# Browser 2 (user2@example.com)
- Should only see User 2's tasks
- Should NOT see User 1's tasks
```

**Expected Result:**
- Each user sees only their own tasks
- No cross-user data visible
- Complete isolation maintained

---

## Development Workflow

### Making Changes

**1. Modify Components:**
```bash
# Edit a component
code components/tasks/TaskList.tsx

# Changes hot-reload automatically
# Check browser - updates without refresh
```

**2. Add New Pages:**
```bash
# Create new page
mkdir -p app/about
touch app/about/page.tsx

# Navigate to http://localhost:3000/about
```

**3. Update Styles:**
```bash
# Edit Tailwind config
code tailwind.config.ts

# Or edit global styles
code app/globals.css
```

### Building for Production

**Build the application:**
```bash
npm run build
```

**Expected output:**
```
Route (app)                              Size     First Load JS
┌ ○ /                                    1.2 kB         80 kB
├ ○ /signin                              2.5 kB         82 kB
├ ○ /signup                              2.5 kB         82 kB
└ ○ /tasks                               3.8 kB         84 kB
```

**Start production server:**
```bash
npm start
```

---

## Troubleshooting

### Issue: "Cannot connect to backend"

**Symptoms:**
- API requests fail
- Network errors in console
- Tasks don't load

**Possible Causes:**
1. Backend not running
2. Wrong API URL in environment
3. CORS not configured on backend

**Solutions:**

**1. Verify backend is running:**
```bash
curl http://localhost:8000/health
# Should return 200 OK
```

**2. Check environment variable:**
```bash
# In frontend directory
cat .env.local | grep NEXT_PUBLIC_API_URL
# Should show: NEXT_PUBLIC_API_URL=http://localhost:8000
```

**3. Check CORS configuration:**
```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: "Authentication not working"

**Symptoms:**
- Cannot sign in
- Redirected to signin repeatedly
- 401 errors on API requests

**Possible Causes:**
1. Better Auth not configured correctly
2. Token not being stored
3. Token not being sent with requests

**Solutions:**

**1. Verify Better Auth configuration:**
```typescript
// lib/auth.ts
console.log('API URL:', process.env.NEXT_PUBLIC_API_URL)
// Should log correct backend URL
```

**2. Check browser console:**
```
Open DevTools → Console
Look for authentication errors
Check Network tab for failed requests
```

**3. Verify token in requests:**
```
Open DevTools → Network tab
Click on API request
Check Headers → Authorization
Should see: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Issue: "Tasks not displaying"

**Symptoms:**
- Empty task list when tasks exist
- Loading spinner never stops
- No error messages

**Possible Causes:**
1. API endpoint incorrect
2. User ID mismatch
3. Backend returning wrong data

**Solutions:**

**1. Check API request:**
```
Open DevTools → Network tab
Look for /api/{user_id}/tasks request
Check response data
```

**2. Verify user ID:**
```typescript
// Add console.log in component
console.log('User ID:', user?.user_id)
console.log('API URL:', `/api/${user?.user_id}/tasks`)
```

**3. Test backend directly:**
```bash
# Get token from signin
TOKEN="<your-jwt-token>"
USER_ID="<your-user-id>"

curl http://localhost:8000/api/$USER_ID/tasks \
  -H "Authorization: Bearer $TOKEN"

# Should return task array
```

### Issue: "Page not found (404)"

**Symptoms:**
- Navigating to route shows 404
- Route exists in code

**Possible Causes:**
1. File not named correctly
2. Directory structure wrong
3. Development server needs restart

**Solutions:**

**1. Verify file structure:**
```bash
# Should have page.tsx in route directory
ls -la app/tasks/
# Should show: page.tsx

# NOT: tasks.tsx or TasksPage.tsx
```

**2. Restart development server:**
```bash
# Stop server (Ctrl+C)
# Start again
npm run dev
```

### Issue: "Styles not applying"

**Symptoms:**
- Tailwind classes not working
- Components look unstyled

**Possible Causes:**
1. Tailwind not configured
2. Classes not in content paths
3. Build cache issue

**Solutions:**

**1. Verify Tailwind config:**
```typescript
// tailwind.config.ts
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  // ...
}
```

**2. Clear cache and rebuild:**
```bash
rm -rf .next
npm run dev
```

---

## API Integration Examples

### Fetching Tasks

```typescript
import { useEffect, useState } from 'react'
import apiClient from '@/lib/api-client'

export function TaskList() {
  const [tasks, setTasks] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    async function fetchTasks() {
      try {
        const data = await apiClient.get(`/api/${user.user_id}/tasks`)
        setTasks(data.data)
      } catch (error) {
        console.error('Failed to fetch tasks:', error)
      } finally {
        setIsLoading(false)
      }
    }

    if (user) {
      fetchTasks()
    }
  }, [user])

  if (isLoading) return <LoadingSpinner />

  return (
    <div>
      {tasks.map((task) => (
        <TaskItem key={task.id} task={task} />
      ))}
    </div>
  )
}
```

### Creating a Task

```typescript
async function handleCreateTask(title: string, description: string) {
  try {
    const response = await apiClient.post(`/api/${user.user_id}/tasks`, {
      title,
      description,
    })

    const newTask = response.data
    setTasks([...tasks, newTask])
    setTitle('')
    setDescription('')
  } catch (error) {
    console.error('Failed to create task:', error)
    setError('Failed to create task')
  }
}
```

---

## Quick Reference

### Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| NEXT_PUBLIC_API_URL | Yes | `http://localhost:8000` |
| BETTER_AUTH_SECRET | Yes | (from Feature 1) |

### Common Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm start                # Start production server

# Utilities
npm run lint             # Run linter
npm run type-check       # Check TypeScript types
```

### Port Configuration

| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |

### Key Routes

| Route | Purpose | Protected |
|-------|---------|-----------|
| / | Landing page | No |
| /signup | User registration | No |
| /signin | User login | No |
| /tasks | Task management | Yes |

---

## Next Steps

Now that the frontend is set up, you can:

1. **Customize Styling** - Modify Tailwind configuration and component styles
2. **Add Features** - Implement additional functionality (search, filters, etc.)
3. **Improve UX** - Add animations, transitions, better loading states
4. **Deploy** - Deploy to Vercel, Netlify, or other hosting platform

For more information, see:
- [Implementation Plan](./plan.md)
- [Data Model](./data-model.md)
- [Research Findings](./research.md)

---

**End of Quickstart Guide**
