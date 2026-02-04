'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import apiClient from '@/lib/api-client'

interface User {
  user_id: string
  email: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  signup: (email: string, password: string) => Promise<void>
  signin: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check if user is authenticated on mount
    const token = localStorage.getItem('auth_token')
    if (token) {
      // Verify token by fetching current user
      apiClient.get('/auth/me')
        .then(response => {
          setUser(response.data)
        })
        .catch(() => {
          localStorage.removeItem('auth_token')
        })
        .finally(() => {
          setIsLoading(false)
        })
    } else {
      setIsLoading(false)
    }
  }, [])

  const signup = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/signup', { email, password })
    const { token, user: userData } = response.data

    // Store token
    localStorage.setItem('auth_token', token)
    setUser(userData)
  }

  const signin = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/signin', { email, password })
    const { token, user: userData } = response.data

    // Store token
    localStorage.setItem('auth_token', token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('auth_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        signup,
        signin,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
