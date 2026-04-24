import React, { createContext, useContext, useState, useEffect } from 'react'
import { buildApiUrl } from '../utils/apiConfig'

const AuthContext = createContext()
const AUTH_TOKEN_STORAGE_KEY = 'googleToken'
const AUTH_USER_STORAGE_KEY = 'googleUser'

function clearStoredAuth() {
  sessionStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
  sessionStorage.removeItem(AUTH_USER_STORAGE_KEY)
  localStorage.removeItem(AUTH_TOKEN_STORAGE_KEY)
  localStorage.removeItem(AUTH_USER_STORAGE_KEY)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [userStats, setUserStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedToken = sessionStorage.getItem(AUTH_TOKEN_STORAGE_KEY)
    const savedUser = sessionStorage.getItem(AUTH_USER_STORAGE_KEY)

    if (savedToken && savedUser) {
      try {
        setToken(savedToken)
        setUser(JSON.parse(savedUser))
        fetchUserStats(savedToken)
      } catch {
        clearStoredAuth()
      }
    }

    setLoading(false)
  }, [])

  const fetchUserStats = async (authToken) => {
    try {
      const response = await fetch(buildApiUrl('/api/accounts/me'), {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        const me = await response.json()
        setUserStats({ user: { user_id: me.uid, uid: me.uid, email: me.email, name: me.name }, usage: {} })
      } else if (response.status === 401) {
        logout()
        return
      } else {
        setUserStats(null)
      }
    } catch (error) {
      console.error('Error fetching user:', error)
    }
  }

  const login = (googleToken, userData) => {
    setToken(googleToken)
    setUser(userData)
    sessionStorage.setItem(AUTH_TOKEN_STORAGE_KEY, googleToken)
    sessionStorage.setItem(AUTH_USER_STORAGE_KEY, JSON.stringify(userData))
    fetchUserStats(googleToken)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    setUserStats(null)
    clearStoredAuth()
  }

  const value = {
    user,
    token,
    userStats,
    loading,
    login,
    logout,
    isAuthenticated: !!user && !!token,
    fetchUserStats
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
