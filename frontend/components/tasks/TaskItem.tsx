'use client'

import React, { useState } from 'react'
import { Task, useTasks } from '@/hooks/useTasks'
import { Button } from '../ui/Button'
import { EditTaskForm } from './EditTaskForm'

interface TaskItemProps {
  task: Task
}

export function TaskItem({ task }: TaskItemProps) {
  const { updateTask, deleteTask, toggleCompletion } = useTasks()
  const [isEditing, setIsEditing] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const handleToggleCompletion = async () => {
    try {
      await toggleCompletion(task.id)
    } catch (err) {
      console.error('Failed to toggle completion:', err)
    }
  }

  const handleEdit = async (data: { title?: string; description?: string; completed?: boolean; priority?: string; due_date?: string }) => {
    await updateTask(task.id, data)
    setIsEditing(false)
  }

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return
    }

    setIsDeleting(true)
    try {
      await deleteTask(task.id)
    } catch (err) {
      console.error('Failed to delete task:', err)
      setIsDeleting(false)
    }
  }

  // Check if task is overdue
  const isOverdue = task.due_date && !task.completed && new Date(task.due_date) < new Date();

  // Determine priority color
  const priorityColors = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    low: 'bg-green-100 text-green-800 border-green-200'
  };

  const priorityColor = priorityColors[task.priority as keyof typeof priorityColors] || priorityColors.medium;

  if (isEditing) {
    return (
      <div className={`bg-white p-4 rounded-lg shadow-md ${isOverdue ? 'border-l-4 border-l-red-500' : ''}`}>
        <EditTaskForm
          task={task}
          onSave={handleEdit}
          onCancel={() => setIsEditing(false)}
        />
      </div>
    )
  }

  return (
    <div className={`bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow ${isOverdue ? 'border-l-4 border-l-red-500' : ''}`}>
      <div className="flex items-start gap-3">
        <input
          type="checkbox"
          checked={task.completed}
          onChange={handleToggleCompletion}
          className="mt-1 h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer"
        />

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className={`text-lg font-medium ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {task.title}
            </h3>
            <span className={`text-xs px-2 py-1 rounded-full border ${priorityColor}`}>
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
            </span>
          </div>

          {task.description && (
            <p className={`mt-1 text-sm ${task.completed ? 'line-through text-gray-400' : 'text-gray-600'}`}>
              {task.description}
            </p>
          )}

          <div className="mt-2 flex flex-wrap gap-4 text-xs text-gray-400">
            <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
            {task.due_date && (
              <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
                Due: {new Date(task.due_date).toLocaleDateString()}
                {isOverdue && !task.completed && ' (OVERDUE)'}
              </span>
            )}
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            variant="secondary"
            onClick={() => setIsEditing(true)}
            className="text-sm px-3 py-1"
          >
            Edit
          </Button>
          <Button
            variant="danger"
            onClick={handleDelete}
            loading={isDeleting}
            className="text-sm px-3 py-1"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  )
}
