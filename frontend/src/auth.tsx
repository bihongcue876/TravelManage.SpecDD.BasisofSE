import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react'

export type UserRole = 'admin' | 'frontdesk' | 'finance'

export interface User {
  id: number
  username: string
  name: string
  role: UserRole
  email: string | null
  phone: string | null
}

interface AuthContextType {
  user: User | null
  token: string | null
  loading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
  hasRole: (...roles: UserRole[]) => boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

async function fetchJson(path: string, options?: RequestInit) {
  const token = localStorage.getItem('access_token')
  const res = await fetch(path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options?.headers,
    },
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }))
    if (res.status === 401) {
      localStorage.removeItem('access_token')
    }
    throw new Error((err as any).detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('access_token'))
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async (tok: string) => {
    try {
      const data = await fetchJson('/api/auth/me', {
        headers: { Authorization: `Bearer ${tok}` },
      })
      setUser({
        id: data.id,
        username: data.username,
        name: data.name,
        role: data.role as UserRole,
        email: data.email ?? null,
        phone: data.phone ?? null,
      })
    } catch {
      // Token 无效或过期，清除登录状态
      localStorage.removeItem('access_token')
      setToken(null)
      setUser(null)
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchUser(token).finally(() => setLoading(false))
    } else {
      setUser(null)
      setLoading(false)
    }
  }, [token, fetchUser])

  const login = async (username: string, password: string) => {
    const data = await fetchJson('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    localStorage.setItem('access_token', data.access_token)
    setToken(data.access_token)
    // 立即设置基本信息，避免 loading 窗口期闪烁
    setUser({
      id: 0,
      username: data.username,
      name: data.name,
      role: data.role as UserRole,
      email: null,
      phone: null,
    })
    // 异步获取完整用户信息（含真实 id）
    fetchUser(data.access_token)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setToken(null)
    setUser(null)
  }

  const hasRole = (...roles: UserRole[]) => {
    if (!user) return false
    return roles.includes(user.role)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        loading,
        login,
        logout,
        isAuthenticated: !!user,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return ctx
}
