'use client'

import React, { useState } from 'react'
import { Task } from '@/hooks/useTasks'
import { Button } from '../ui/Button'
import { Input, Textarea } from '../ui/Input'

interface EditTaskFormProps {
  task: Task
  onSave: (data: { title?: string; description?: string; completed?: boolean; priority?: string; due_date?: string }) => Promise<void>
  onCancel: () => void
}

export function EditTaskForm({ task, onSave, onCancel }: EditTaskFormProps) {
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description || '')
  const [completed, setCompleted] = useState(task.completed)
  const [priority, setPriority] = useState(task.priority || 'medium')
  const [dueDate, setDueDate] = useState(task.due_date || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const titleCharsLeft = 255 - title.length
  const descriptionCharsLeft = 1000 - description.length

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    if (title.length > 255) {
      setError('Title must be 255 characters or less')
      return
    }

    if (description.length > 1000) {
      setError('Description must be 1000 characters or less')
      return
    }

    setLoading(true)
    setError('')

    try {
      await onSave({
        title: title.trim(),
        description: description.trim() || undefined,
        completed,
        priority,
        due_date: dueDate || undefined
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update task')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-md">
      <div className="space-y-4">
        <Input
          label="Title"
          required
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={255}
          helperText={`${titleCharsLeft} characters remaining`}
        />

        <Textarea
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={3}
          maxLength={1000}
          helperText={`${descriptionCharsLeft} characters remaining`}
        />
      </div>

      <div className="space-y-4">
        <div>
          <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <select
            id="priority"
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
            Due Date
          </label>
          <input
            type="date"
            id="dueDate"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="completed"
            checked={completed}
            onChange={(e) => setCompleted(e.target.checked)}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="completed" className="text-sm font-medium text-gray-700">
            Mark as completed
          </label>
        </div>
      </div>

      {error && (
        <div className="col-span-2">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div className="col-span-2 flex gap-2">
        <Button type="submit" loading={loading}>
          Save Changes
        </Button>
        <Button type="button" variant="secondary" onClick={onCancel} disabled={loading}>
          Cancel
        </Button>
      </div>
    </form>
  )
}
