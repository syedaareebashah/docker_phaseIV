---
name: frontend-skill
description: Build responsive pages, reusable components, layouts, and styling with Next.js App Router and Tailwind CSS. Use for all UI development tasks.
---

# Frontend Skill – Build pages, components, layout, styling

## Instructions

1. **Page Structure (Next.js App Router)**
   - Create page.tsx files in app directory
   - Implement proper metadata and SEO
   - Use server/client components appropriately
   - Handle loading and error states

2. **Component Development**
   - Build reusable React components
   - Follow single responsibility principle
   - Use TypeScript for type safety
   - Implement proper prop validation
   - Extract repeated UI into components

3. **Layout Implementation**
   - Design responsive grid systems
   - Use flexbox and CSS Grid
   - Implement mobile-first approach
   - Create consistent spacing and alignment
   - Build navigation and header/footer

4. **Styling with Tailwind CSS**
   - Use utility-first classes
   - Implement responsive breakpoints (sm, md, lg, xl)
   - Apply consistent color palette
   - Use Tailwind's spacing scale
   - Create custom configurations when needed

5. **State Management**
   - Use useState for local state
   - Implement useEffect for side effects
   - Manage forms with controlled components
   - Handle API data with proper loading states

## Best Practices

- **Component Organization**: One component per file, named exports
- **Responsive Design**: Mobile-first, test all breakpoints
- **Accessibility**: Proper semantic HTML, ARIA labels, keyboard navigation
- **Performance**: Lazy load images, code splitting, memoization
- **Consistency**: Reuse components, follow naming conventions
- **Clean Code**: Remove unused imports, format with Prettier

## File Structure Example
```
app/
├── layout.tsx          # Root layout
├── page.tsx            # Home page
├── tasks/
│   ├── page.tsx        # Tasks list page
│   └── [id]/
│       └── page.tsx    # Task detail page
components/
├── ui/
│   ├── Button.tsx
│   ├── Input.tsx
│   └── Card.tsx
└── TaskList.tsx
```

## Component Template
```tsx
// components/TaskCard.tsx
interface TaskCardProps {
  title: string;
  description?: string;
  completed: boolean;
  onToggle: () => void;
  onDelete: () => void;
}

export function TaskCard({
  title,
  description,
  completed,
  onToggle,
  onDelete
}: TaskCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className={`text-lg font-semibold ${completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
            {title}
          </h3>
          {description && (
            <p className="mt-2 text-sm text-gray-600">{description}</p>
          )}
        </div>
        <div className="flex gap-2 ml-4">
          <button
            onClick={onToggle}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            {completed ? 'Undo' : 'Complete'}
          </button>
          <button
            onClick={onDelete}
            className="px-3 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
```

## Page Template
```tsx
// app/tasks/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { TaskCard } from '@/components/TaskCard';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
}

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('jwt_token');
      const response = await fetch('/api/tasks', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch tasks');
      
      const data = await response.json();
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">{error}</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">My Tasks</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            {...task}
            onToggle={() => handleToggle(task.id)}
            onDelete={() => handleDelete(task.id)}
          />
        ))}
      </div>
    </div>
  );
}
```

## Responsive Styling Patterns
```tsx
// Mobile-first responsive classes
<div className="
  w-full           /* Mobile: full width */
  md:w-1/2         /* Tablet: half width */
  lg:w-1/3         /* Desktop: third width */
  p-4              /* Mobile: padding 1rem */
  md:p-6           /* Tablet: padding 1.5rem */
  lg:p-8           /* Desktop: padding 2rem */
">
  Content
</div>
```

## Form Handling
```tsx
const [formData, setFormData] = useState({ title: '', description: '' });

const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  // API call with formData
};

<form onSubmit={handleSubmit} className="space-y-4">
  <input
    type="text"
    value={formData.title}
    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
    className="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
    placeholder="Task title"
  />
  <button
    type="submit"
    className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors"
  >
    Create Task
  </button>
</form>
```

## Common Tailwind Patterns

- **Container**: `container mx-auto px-4`
- **Card**: `bg-white rounded-lg shadow-md p-6`
- **Button Primary**: `bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600`
- **Input**: `w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500`
- **Grid**: `grid gap-4 md:grid-cols-2 lg:grid-cols-3`
- **Flex Center**: `flex items-center justify-center`

Use this skill for creating all frontend pages, components, layouts, and styling in the Next.js application.