# Research Findings: Frontend Application & Integration

**Feature ID:** 3-frontend-app-integration
**Version:** 1.0.0
**Created:** 2026-02-03

---

## Overview

This document consolidates research findings for technical decisions made during the planning phase of the Frontend Application & Integration feature. Each decision includes rationale, alternatives considered, and implementation guidance.

---

## R1: Next.js App Router Patterns

### Decision
Use Next.js 16+ App Router with route groups for organization, middleware for authentication checks, and layouts for shared UI structure.

### Rationale
- **Modern Architecture:** App Router is the future of Next.js, with better performance and DX
- **Built-in Features:** Loading states, error boundaries, layouts out of the box
- **Server Components:** Better performance with server-side rendering by default
- **Simplified Routing:** File-system based routing with intuitive structure

### Alternatives Considered

**1. Pages Router**
- Pros: More mature, more examples available, familiar to developers
- Cons: Legacy approach, missing modern features, more boilerplate
- Verdict: Rejected - App Router is the recommended approach for new projects

**2. React Router (SPA)**
- Pros: Client-side only, simpler deployment
- Cons: Worse SEO, slower initial load, no server-side rendering
- Verdict: Rejected - Next.js provides better performance and features

**3. Remix**
- Pros: Modern framework, excellent data loading patterns
- Cons: Different ecosystem, team unfamiliar, not specified in requirements
- Verdict: Rejected - Next.js specified in requirements

### Implementation Guidance

**Directory Structure:**
```
app/
├── (auth)/              # Route group for auth pages
│   ├── layout.tsx       # Auth layout
│   ├── signin/
│   │   └── page.tsx
│   └── signup/
│       └── page.tsx
├── (app)/               # Route group for protected pages
│   ├── layout.tsx       # App layout with nav
│   └── tasks/
│       └── page.tsx
├── layout.tsx           # Root layout
└── page.tsx             # Landing page
```

**Route Groups:**
- Use `(auth)` and `(app)` to organize routes without affecting URL structure
- Each group can have its own layout
- Keeps related pages together

**Layouts:**
```typescript
// app/(app)/layout.tsx
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <nav>{/* Navigation with logout */}</nav>
      <main>{children}</main>
    </div>
  )
}
```

**Loading States:**
```typescript
// app/tasks/loading.tsx
export default function Loading() {
  return <LoadingSpinner />
}
```

**Error Boundaries:**
```typescript
// app/tasks/error.tsx
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  )
}
```

### References
- Next.js App Router: https://nextjs.org/docs/app
- Route Groups: https://nextjs.org/docs/app/building-your-application/routing/route-groups

---

## R2: Better Auth React Integration

### Decision
Use Better Auth React hooks for authentication state management, with Better Auth handling token storage and session persistence.

### Rationale
- **Integrated Solution:** Better Auth already configured in Feature 1
- **React Hooks:** Clean, modern API for React applications
- **Token Management:** Handles JWT storage and refresh automatically
- **Type Safety:** TypeScript support out of the box

### Implementation Guidance

**Installation:**
```bash
npm install better-auth
```

**Configuration (lib/auth.ts):**
```typescript
import { createAuthClient } from 'better-auth/react'

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  credentials: 'include', // For cookies
})

export const { useSession, signIn, signUp, signOut } = authClient
```

**Usage in Components:**
```typescript
'use client'

import { useSession, signIn, signOut } from '@/lib/auth'

export function AuthButton() {
  const { data: session, status } = useSession()

  if (status === 'loading') {
    return <LoadingSpinner />
  }

  if (session) {
    return (
      <button onClick={() => signOut()}>
        Sign out ({session.user.email})
      </button>
    )
  }

  return <button onClick={() => signIn()}>Sign in</button>
}
```

**Authentication Context:**
```typescript
'use client'

import { createContext, useContext } from 'react'
import { useSession } from '@/lib/auth'

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, status } = useSession()

  const value = {
    isAuthenticated: !!session,
    isLoading: status === 'loading',
    user: session?.user || null,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
```

### References
- Better Auth React: https://www.better-auth.com/docs/integrations/react
- Better Auth Hooks: https://www.better-auth.com/docs/api/react-hooks

---

## R3: Protected Route Implementation

### Decision
Use component-level route protection with redirect for unauthenticated users, checking auth state before rendering protected content.

### Rationale
- **Simple Implementation:** Easy to understand and maintain
- **Flexible:** Can be applied to any page or component
- **User-Friendly:** Clear redirect flow for unauthenticated users
- **No Flash:** Loading state prevents flash of protected content

### Alternatives Considered

**1. Middleware-Based Protection**
- Pros: Centralized, runs before page render
- Cons: More complex setup, harder to customize per-route
- Verdict: Acceptable but component-level is simpler for this app

**2. Higher-Order Component (HOC)**
- Pros: Reusable wrapper pattern
- Cons: Older pattern, less idiomatic in modern React
- Verdict: Rejected - hooks and components are more modern

**3. Server-Side Protection**
- Pros: More secure, no client-side bypass
- Cons: More complex, requires server-side session management
- Verdict: Rejected - client-side is sufficient with JWT validation on backend

### Implementation Guidance

**Protected Route Component:**
```typescript
'use client'

import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/signin')
    }
  }, [isAuthenticated, isLoading, router])

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return null // Will redirect
  }

  return <>{children}</>
}
```

**Usage:**
```typescript
// app/tasks/page.tsx
import { ProtectedRoute } from '@/components/ProtectedRoute'

export default function TasksPage() {
  return (
    <ProtectedRoute>
      <TaskList />
    </ProtectedRoute>
  )
}
```

**Alternative: Layout-Level Protection:**
```typescript
// app/(app)/layout.tsx
'use client'

import { ProtectedRoute } from '@/components/ProtectedRoute'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <div>
        <nav>{/* Navigation */}</nav>
        <main>{children}</main>
      </div>
    </ProtectedRoute>
  )
}
```

### References
- Next.js Authentication: https://nextjs.org/docs/app/building-your-application/authentication
- React Router Guards: https://reactrouter.com/en/main/start/concepts#route-guards

---

## R4: API Client with Axios Interceptors

### Decision
Use Axios with request/response interceptors for centralized API communication, automatic token attachment, and consistent error handling.

### Rationale
- **Interceptors:** Clean way to modify all requests/responses
- **Automatic Token:** Attach JWT to every request without manual code
- **Error Handling:** Centralized 401/403 handling with redirects
- **Type Safety:** Can be typed with TypeScript

### Implementation Guidance

**Installation:**
```bash
npm install axios
```

**API Client Setup (lib/api-client.ts):**
```typescript
import axios, { AxiosInstance } from 'axios'
import { authClient } from './auth'

const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - attach JWT token
apiClient.interceptors.request.use(
  async (config) => {
    const session = await authClient.getSession()
    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout and redirect
      await authClient.signOut()
      window.location.href = '/signin'
    } else if (error.response?.status === 403) {
      // Forbidden - show error message
      console.error('Access forbidden:', error.response.data)
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

**API Methods:**
```typescript
// Task API methods
export const taskAPI = {
  getTasks: (userId: string) =>
    apiClient.get(`/api/${userId}/tasks`).then((res) => res.data),

  createTask: (userId: string, data: { title: string; description?: string }) =>
    apiClient.post(`/api/${userId}/tasks`, data).then((res) => res.data),

  updateTask: (userId: string, taskId: string, data: Partial<Task>) =>
    apiClient.put(`/api/${userId}/tasks/${taskId}`, data).then((res) => res.data),

  deleteTask: (userId: string, taskId: string) =>
    apiClient.delete(`/api/${userId}/tasks/${taskId}`),

  toggleCompletion: (userId: string, taskId: string) =>
    apiClient.patch(`/api/${userId}/tasks/${taskId}/complete`).then((res) => res.data),
}
```

**Usage in Components:**
```typescript
import { taskAPI } from '@/lib/api-client'

async function handleCreateTask(title: string, description: string) {
  try {
    const newTask = await taskAPI.createTask(userId, { title, description })
    setTasks([...tasks, newTask])
  } catch (error) {
    console.error('Failed to create task:', error)
    setError('Failed to create task')
  }
}
```

### References
- Axios Documentation: https://axios-http.com/
- Axios Interceptors: https://axios-http.com/docs/interceptors

---

## R5: Optimistic UI Updates

### Decision
Implement optimistic updates for task operations (toggle completion, delete) with rollback on error, providing immediate feedback while maintaining data consistency.

### Rationale
- **Better UX:** Immediate visual feedback, feels faster
- **Perceived Performance:** App feels more responsive
- **Rollback Safety:** Can revert if backend operation fails
- **Common Pattern:** Industry standard for modern web apps

### Implementation Guidance

**Optimistic Toggle Pattern:**
```typescript
async function handleToggleCompletion(taskId: string) {
  // Find the task
  const task = tasks.find((t) => t.id === taskId)
  if (!task) return

  // Optimistically update UI
  const optimisticTasks = tasks.map((t) =>
    t.id === taskId ? { ...t, completed: !t.completed } : t
  )
  setTasks(optimisticTasks)

  try {
    // Confirm with backend
    const updatedTask = await taskAPI.toggleCompletion(userId, taskId)

    // Update with backend response (in case of any differences)
    setTasks((current) =>
      current.map((t) => (t.id === taskId ? updatedTask : t))
    )
  } catch (error) {
    // Rollback on error
    setTasks(tasks) // Restore original state
    setError('Failed to update task')
  }
}
```

**Optimistic Delete Pattern:**
```typescript
async function handleDeleteTask(taskId: string) {
  // Store original state for rollback
  const originalTasks = tasks

  // Optimistically remove from UI
  setTasks(tasks.filter((t) => t.id !== taskId))

  try {
    // Confirm with backend
    await taskAPI.deleteTask(userId, taskId)
    // Success - optimistic update was correct
  } catch (error) {
    // Rollback on error
    setTasks(originalTasks)
    setError('Failed to delete task')
  }
}
```

**Non-Optimistic Create Pattern:**
```typescript
// Don't use optimistic updates for create - wait for backend ID
async function handleCreateTask(title: string, description: string) {
  setIsSubmitting(true)

  try {
    const newTask = await taskAPI.createTask(userId, { title, description })
    setTasks([...tasks, newTask]) // Add with real ID from backend
    setIsSubmitting(false)
  } catch (error) {
    setError('Failed to create task')
    setIsSubmitting(false)
  }
}
```

**When to Use Optimistic Updates:**
- ✅ Toggle operations (completion status)
- ✅ Delete operations
- ✅ Simple updates (title, description)
- ❌ Create operations (need backend-generated ID)
- ❌ Complex operations with validation

### References
- Optimistic UI: https://www.apollographql.com/docs/react/performance/optimistic-ui/
- React Query Optimistic Updates: https://tanstack.com/query/latest/docs/react/guides/optimistic-updates

---

## Summary

All research topics have been resolved with concrete implementation guidance. Key decisions:

1. **Next.js App Router:** Modern routing with layouts, loading states, error boundaries
2. **Better Auth React:** Integrated authentication with hooks and automatic token management
3. **Component-Level Protection:** Simple, flexible route protection with redirects
4. **Axios Interceptors:** Centralized API client with automatic token attachment and error handling
5. **Optimistic Updates:** Immediate UI feedback with rollback on error

These decisions provide a solid foundation for building a responsive, user-friendly frontend that integrates seamlessly with Features 1 and 2.

---

**End of Research Findings**
