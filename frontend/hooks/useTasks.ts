'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import apiClient from '@/lib/api-client'

export interface Task {
  id: string
  user_id: string
  title: string
  description: string | null
  completed: boolean
  priority: string
  due_date: string | null
  created_at: string
  updated_at: string
}

export interface CreateTaskData {
  title: string
  description?: string
  priority?: string
  due_date?: string
}

export interface UpdateTaskData {
  title?: string
  description?: string
  completed?: boolean
  priority?: string
  due_date?: string
}

export function useTasks() {
  const { user } = useAuth()
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchTasks = useCallback(async () => {
    if (!user?.user_id) return

    setLoading(true)
    setError(null)

    try {
      const response = await apiClient.get(`/api/${user.user_id}/tasks`)
      setTasks(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch tasks')
    } finally {
      setLoading(false)
    }
  }, [user?.user_id])

  const createTask = useCallback(async (data: CreateTaskData) => {
    if (!user?.user_id) return

    setError(null)

    try {
      const response = await apiClient.post(`/api/${user.user_id}/tasks`, data)
      setTasks(prev => [response.data, ...prev])
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task')
      throw err
    }
  }, [user?.user_id])

  const updateTask = useCallback(async (taskId: string, data: UpdateTaskData) => {
    if (!user?.user_id) return

    setError(null)

    try {
      const response = await apiClient.put(`/api/${user.user_id}/tasks/${taskId}`, data)
      setTasks(prev => prev.map(task => task.id === taskId ? response.data : task))
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update task')
      throw err
    }
  }, [user?.user_id])

  const deleteTask = useCallback(async (taskId: string) => {
    if (!user?.user_id) return

    setError(null)

    // Optimistic update
    const previousTasks = tasks
    setTasks(prev => prev.filter(task => task.id !== taskId))

    try {
      await apiClient.delete(`/api/${user.user_id}/tasks/${taskId}`)
    } catch (err: any) {
      // Rollback on error
      setTasks(previousTasks)
      setError(err.response?.data?.detail || 'Failed to delete task')
      throw err
    }
  }, [user?.user_id, tasks])

  const toggleCompletion = useCallback(async (taskId: string) => {
    if (!user?.user_id) return

    setError(null)

    // Optimistic update
    const previousTasks = tasks
    setTasks(prev => prev.map(task =>
      task.id === taskId ? { ...task, completed: !task.completed } : task
    ))

    try {
      const response = await apiClient.patch(`/api/${user.user_id}/tasks/${taskId}/complete`)
      setTasks(prev => prev.map(task => task.id === taskId ? response.data : task))
    } catch (err: any) {
      // Rollback on error
      setTasks(previousTasks)
      setError(err.response?.data?.detail || 'Failed to toggle task completion')
      throw err
    }
  }, [user?.user_id, tasks])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleCompletion
  }
}
