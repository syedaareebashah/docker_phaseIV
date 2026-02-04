# Data Model: Frontend Application & Integration

**Feature ID:** 3-frontend-app-integration
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This document defines the frontend data structures, state models, and component architecture for the Frontend Application & Integration feature. Unlike backend data models, this focuses on UI state, component props, and client-side data flow.

---

## State Models

### Authentication State

**Description:** Manages user authentication status and user information

**Structure:**
```typescript
interface AuthState {
  isAuthenticated: boolean
  isLoading: boolean
  user: User | null
  error: string | null
}

interface User {
  user_id: string
  email: string
  created_at: string
}
```

**State Transitions:**
```
[Unauthenticated]
    |
    | signup/signin success
    v
[Authenticated]
    |
    | logout / token expiration
    v
[Unauthenticated]
```

**Managed By:** AuthContext (React Context)

**Persistence:** Better Auth handles token persistence

---

### Task State

**Description:** Manages task list and individual task data

**Structure:**
```typescript
interface TaskState {
  tasks: Task[]
  isLoading: boolean
  error: string | null
  selectedTask: Task | null
}

interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}
```

**State Transitions:**
```
[Empty List]
    |
    | fetch tasks
    v
[Loading]
    |
    | success
    v
[Tasks Loaded]
    |
    | create/update/delete
    v
[Optimistic Update]
    |
    | API confirms
    v
[Tasks Updated]
```

**Managed By:** useTasks hook (React hook)

**Persistence:** Backend API (no local persistence)

---

### Form State

**Description:** Manages form input and validation

**Task Creation Form:**
```typescript
interface CreateTaskFormState {
  title: string
  description: string
  isSubmitting: boolean
  errors: {
    title?: string
    description?: string
  }
}
```

**Task Edit Form:**
```typescript
interface EditTaskFormState {
  title: string
  description: string
  completed: boolean
  isSubmitting: boolean
  errors: {
    title?: string
    description?: string
  }
}
```

**Authentication Forms:**
```typescript
interface AuthFormState {
  email: string
  password: string
  isSubmitting: boolean
  errors: {
    email?: string
    password?: string
    general?: string
  }
}
```

**Managed By:** Local component state (useState)

**Validation Rules:**
- Title: Required, 1-255 characters
- Description: Optional, 0-1000 characters
- Email: Required, valid email format
- Password: Required, meets complexity requirements

---

## Component Architecture

### Page Components

**Landing Page (`/app/page.tsx`)**
- **Purpose:** Entry point, redirects based on auth status
- **Props:** None
- **State:** None (uses auth context)
- **Behavior:** Redirects authenticated users to /tasks, unauthenticated to /signin

**Signup Page (`/app/signup/page.tsx`)**
- **Purpose:** User registration interface
- **Props:** None
- **State:** None (delegates to SignupForm)
- **Children:** SignupForm component

**Signin Page (`/app/signin/page.tsx`)**
- **Purpose:** User login interface
- **Props:** None
- **State:** None (delegates to SigninForm)
- **Children:** SigninForm component

**Tasks Page (`/app/tasks/page.tsx`)**
- **Purpose:** Main task management interface (protected)
- **Props:** None
- **State:** Task list state (via useTasks hook)
- **Children:** TaskList, CreateTaskForm components
- **Protection:** Wrapped in ProtectedRoute

---

### Layout Components

**Root Layout (`/app/layout.tsx`)**
- **Purpose:** Global layout wrapper
- **Props:** children
- **Providers:** AuthProvider
- **Includes:** HTML structure, global styles

**Auth Layout (`/app/(auth)/layout.tsx`)**
- **Purpose:** Layout for authentication pages
- **Props:** children
- **Styling:** Centered form layout
- **Behavior:** Redirects authenticated users away

**App Layout (`/app/(app)/layout.tsx`)**
- **Purpose:** Layout for protected application pages
- **Props:** children
- **Includes:** Navigation, logout button
- **Protection:** Requires authentication

---

### Authentication Components

**SignupForm (`components/auth/SignupForm.tsx`)**
- **Purpose:** User registration form
- **Props:** None
- **State:** Form state (email, password, errors, isSubmitting)
- **Events:** onSubmit
- **Behavior:** Validates input, calls Better Auth signup, redirects on success

**SigninForm (`components/auth/SigninForm.tsx`)**
- **Purpose:** User login form
- **Props:** None
- **State:** Form state (email, password, errors, isSubmitting)
- **Events:** onSubmit
- **Behavior:** Validates input, calls Better Auth signin, redirects on success

---

### Task Components

**TaskList (`components/tasks/TaskList.tsx`)**
- **Purpose:** Display list of tasks
- **Props:**
  ```typescript
  interface TaskListProps {
    tasks: Task[]
    isLoading: boolean
    error: string | null
    onEdit: (task: Task) => void
    onDelete: (taskId: string) => void
    onToggleComplete: (taskId: string) => void
  }
  ```
- **State:** None (receives data via props)
- **Children:** TaskItem components
- **Behavior:** Maps tasks to TaskItem, shows empty state if no tasks

**TaskItem (`components/tasks/TaskItem.tsx`)**
- **Purpose:** Display individual task
- **Props:**
  ```typescript
  interface TaskItemProps {
    task: Task
    onEdit: () => void
    onDelete: () => void
    onToggleComplete: () => void
  }
  ```
- **State:** Edit mode (boolean)
- **Behavior:** Shows task details, provides action buttons, switches to edit mode

**CreateTaskForm (`components/tasks/CreateTaskForm.tsx`)**
- **Purpose:** Form to create new task
- **Props:**
  ```typescript
  interface CreateTaskFormProps {
    onSuccess: (task: Task) => void
  }
  ```
- **State:** Form state (title, description, errors, isSubmitting)
- **Events:** onSubmit
- **Behavior:** Validates input, calls API, clears form on success

**EditTaskForm (`components/tasks/EditTaskForm.tsx`)**
- **Purpose:** Form to edit existing task
- **Props:**
  ```typescript
  interface EditTaskFormProps {
    task: Task
    onSuccess: (task: Task) => void
    onCancel: () => void
  }
  ```
- **State:** Form state (title, description, completed, errors, isSubmitting)
- **Events:** onSubmit, onCancel
- **Behavior:** Pre-fills with task data, validates input, calls API

---

### UI Components

**Button (`components/ui/Button.tsx`)**
- **Purpose:** Reusable button component
- **Props:**
  ```typescript
  interface ButtonProps {
    children: React.ReactNode
    onClick?: () => void
    type?: 'button' | 'submit' | 'reset'
    variant?: 'primary' | 'secondary' | 'danger'
    disabled?: boolean
    isLoading?: boolean
  }
  ```
- **Behavior:** Renders button with appropriate styling, shows loading spinner if isLoading

**Input (`components/ui/Input.tsx`)**
- **Purpose:** Reusable input component
- **Props:**
  ```typescript
  interface InputProps {
    label: string
    type?: 'text' | 'email' | 'password'
    value: string
    onChange: (value: string) => void
    error?: string
    placeholder?: string
    required?: boolean
  }
  ```
- **Behavior:** Renders labeled input with error display

**LoadingSpinner (`components/ui/LoadingSpinner.tsx`)**
- **Purpose:** Loading indicator
- **Props:**
  ```typescript
  interface LoadingSpinnerProps {
    size?: 'small' | 'medium' | 'large'
  }
  ```
- **Behavior:** Renders animated spinner

**ErrorMessage (`components/ui/ErrorMessage.tsx`)**
- **Purpose:** Error display component
- **Props:**
  ```typescript
  interface ErrorMessageProps {
    message: string
    onDismiss?: () => void
  }
  ```
- **Behavior:** Renders error with optional dismiss button

**Toast (`components/ui/Toast.tsx`)**
- **Purpose:** Success/error notification
- **Props:**
  ```typescript
  interface ToastProps {
    message: string
    type: 'success' | 'error' | 'info'
    duration?: number
    onDismiss: () => void
  }
  ```
- **Behavior:** Shows notification, auto-dismisses after duration

---

## Utility Modules

### API Client (`lib/api-client.ts`)

**Purpose:** Centralized HTTP client for backend communication

**Structure:**
```typescript
interface APIClient {
  // Task operations
  getTasks(userId: string): Promise<Task[]>
  getTask(userId: string, taskId: string): Promise<Task>
  createTask(userId: string, data: CreateTaskData): Promise<Task>
  updateTask(userId: string, taskId: string, data: UpdateTaskData): Promise<Task>
  deleteTask(userId: string, taskId: string): Promise<void>
  toggleTaskCompletion(userId: string, taskId: string): Promise<Task>
}

interface CreateTaskData {
  title: string
  description?: string
}

interface UpdateTaskData {
  title?: string
  description?: string
  completed?: boolean
}
```

**Configuration:**
- Base URL from environment variable
- Axios instance with interceptors
- Automatic token attachment
- Error handling

---

### Authentication Context (`contexts/AuthContext.tsx`)

**Purpose:** Provides authentication state and methods throughout app

**Structure:**
```typescript
interface AuthContextValue {
  isAuthenticated: boolean
  isLoading: boolean
  user: User | null
  error: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string) => Promise<void>
  logout: () => void
}
```

**Provider:** Wraps entire application

**Consumers:** Any component needing auth state

---

### Custom Hooks

**useAuth (`hooks/useAuth.ts`)**
- **Purpose:** Access authentication context
- **Returns:** AuthContextValue
- **Usage:** `const { isAuthenticated, user, logout } = useAuth()`

**useTasks (`hooks/useTasks.ts`)**
- **Purpose:** Manage task operations
- **Returns:**
  ```typescript
  interface UseTasksReturn {
    tasks: Task[]
    isLoading: boolean
    error: string | null
    createTask: (data: CreateTaskData) => Promise<void>
    updateTask: (taskId: string, data: UpdateTaskData) => Promise<void>
    deleteTask: (taskId: string) => Promise<void>
    toggleCompletion: (taskId: string) => Promise<void>
    refreshTasks: () => Promise<void>
  }
  ```
- **Usage:** `const { tasks, createTask, isLoading } = useTasks()`

---

## Data Flow Patterns

### Authentication Flow

```
User Action (Login)
    ↓
SigninForm validates input
    ↓
Better Auth signin()
    ↓
Backend validates credentials
    ↓
Backend returns JWT token
    ↓
Better Auth stores token
    ↓
AuthContext updates state
    ↓
UI redirects to /tasks
```

### Task Creation Flow

```
User Action (Create Task)
    ↓
CreateTaskForm validates input
    ↓
useTasks.createTask()
    ↓
API Client POST request
    ↓
Backend creates task
    ↓
Backend returns task data
    ↓
useTasks updates state
    ↓
UI displays new task
```

### Optimistic Update Flow

```
User Action (Toggle Completion)
    ↓
UI immediately updates visual state
    ↓
API Client PATCH request
    ↓
Backend updates task
    ↓
Backend returns updated task
    ↓
UI confirms state matches backend
    ↓
(On error: revert visual state)
```

---

## State Management Strategy

### Local State (useState)
**Use For:**
- Form inputs
- UI toggles (edit mode, modals)
- Component-specific state

### Context State (React Context)
**Use For:**
- Authentication state (global)
- Theme/preferences (if implemented)

### Server State (API)
**Use For:**
- Task data (source of truth is backend)
- User data
- Any persisted data

**Pattern:** Fetch on mount, optimistic updates, confirm with backend

---

## Error Handling

### Error Types

**Network Errors:**
```typescript
interface NetworkError {
  type: 'network'
  message: string
  retryable: boolean
}
```

**Authentication Errors:**
```typescript
interface AuthError {
  type: 'auth'
  status: 401 | 403
  message: string
  action: 'logout' | 'show_message'
}
```

**Validation Errors:**
```typescript
interface ValidationError {
  type: 'validation'
  field: string
  message: string
}
```

**Server Errors:**
```typescript
interface ServerError {
  type: 'server'
  status: 500
  message: string
}
```

### Error Display Strategy

- **Form Errors:** Inline below field
- **Operation Errors:** Toast notification
- **Auth Errors:** Redirect + message
- **Network Errors:** Retry button + message

---

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading:** Load components on demand
2. **Memoization:** Use React.memo for expensive components
3. **Debouncing:** Debounce search/filter inputs
4. **Pagination:** Load tasks in batches (future enhancement)
5. **Caching:** Cache API responses briefly

### Bundle Size

- **Target:** < 200KB initial bundle
- **Strategy:** Code splitting, tree shaking
- **Monitoring:** Webpack bundle analyzer

---

## Testing Data

### Mock User
```typescript
const mockUser: User = {
  user_id: '550e8400-e29b-41d4-a716-446655440000',
  email: 'test@example.com',
  created_at: '2026-02-03T12:00:00Z'
}
```

### Mock Tasks
```typescript
const mockTasks: Task[] = [
  {
    id: '660e8400-e29b-41d4-a716-446655440000',
    user_id: '550e8400-e29b-41d4-a716-446655440000',
    title: 'Complete project documentation',
    description: 'Write comprehensive API docs',
    completed: false,
    created_at: '2026-02-03T12:00:00Z',
    updated_at: '2026-02-03T12:00:00Z'
  },
  {
    id: '770e8400-e29b-41d4-a716-446655440000',
    user_id: '550e8400-e29b-41d4-a716-446655440000',
    title: 'Review pull requests',
    description: null,
    completed: true,
    created_at: '2026-02-03T11:00:00Z',
    updated_at: '2026-02-03T11:30:00Z'
  }
]
```

---

**End of Data Model**
