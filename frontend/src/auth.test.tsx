import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useEffect } from 'react'
import { render, screen, waitFor, act } from '@testing-library/react'
import { AuthProvider, useAuth } from './auth'
import type { ReactNode } from 'react'

// ── 辅助组件 ──

function TestConsumer() {
  const auth = useAuth()
  return (
    <div>
      <div data-testid="loading">{String(auth.loading)}</div>
      <div data-testid="authenticated">{String(auth.isAuthenticated)}</div>
      <div data-testid="user">{auth.user ? JSON.stringify(auth.user) : 'null'}</div>
      <div data-testid="token">{auth.token ?? 'null'}</div>
      {auth.isAuthenticated && (
        <div data-testid="hasRole-admin">{String(auth.hasRole('admin'))}</div>
      )}
      <button data-testid="btn-logout" onClick={auth.logout}>logout</button>
    </div>
  )
}

/** 自动触发 login 的组件（避免 click handler 不 await promise 的问题） */
function LoginAction({ username, password }: { username: string; password: string }) {
  const { login } = useAuth()
  useEffect(() => {
    login(username, password).catch(() => {})
  }, [])
  return null
}

function renderWithAuth(ui: ReactNode) {
  return render(<AuthProvider>{ui}</AuthProvider>)
}

// ── 模拟 fetch ──

const mockFetch = vi.fn()
globalThis.fetch = mockFetch

function mockFetchOnce(data: unknown, ok = true) {
  mockFetch.mockResolvedValueOnce({
    ok,
    status: ok ? 200 : 401,
    json: () => Promise.resolve(data),
  })
}

beforeEach(() => {
  localStorage.clear()
  vi.restoreAllMocks()
})

afterEach(() => {
  localStorage.clear()
})

// ── login 测试 ──

describe('login', () => {
  it('登录成功 → 设置 token、更新 user、isAuthenticated=true', async () => {
    // login() 内部调 1 次 fetchJson('/api/auth/login')
    mockFetchOnce({ access_token: 'test-token-123', username: 'admin', name: '管理员', role: 'admin' })
    // login() 内部调 1 次 fetchUser('/api/auth/me')
    mockFetchOnce({ id: 1, username: 'admin', name: '管理员', role: 'admin', email: 'admin@test.com', phone: null })
    // setToken 触发 useEffect，再调 1 次 fetchUser('/api/auth/me')
    mockFetchOnce({ id: 1, username: 'admin', name: '管理员', role: 'admin', email: null, phone: null })

    renderWithAuth(
      <>
        <TestConsumer />
        <LoginAction username="admin" password="123456" />
      </>
    )

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    })
    expect(localStorage.getItem('access_token')).toBe('test-token-123')
  })

  it('登录失败（401）→ 抛错误、不设置 user', async () => {
    mockFetchOnce({ detail: '用户名或密码错误' }, false)

    renderWithAuth(
      <>
        <TestConsumer />
        <LoginAction username="admin" password="wrong" />
      </>
    )

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
    })
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})

// ── logout 测试 ──

describe('logout', () => {
  it('清除 token、user→null、isAuthenticated=false', async () => {
    localStorage.setItem('access_token', 'test-token')
    mockFetchOnce({ id: 1, username: 'admin', name: '管理员', role: 'admin', email: null, phone: null })

    renderWithAuth(<TestConsumer />)

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true')
    })

    await act(async () => {
      screen.getByTestId('btn-logout').click()
    })

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('user')).toHaveTextContent('null')
    expect(localStorage.getItem('access_token')).toBeNull()
  })
})

// ── hasRole 测试 ──

describe('hasRole', () => {
  it('角色匹配 → true', async () => {
    localStorage.setItem('access_token', 't')
    mockFetchOnce({ id: 1, username: 'admin', name: '管理员', role: 'admin', email: null, phone: null })

    renderWithAuth(<TestConsumer />)

    await waitFor(() => {
      expect(screen.getByTestId('hasRole-admin')).toHaveTextContent('true')
    })
  })
})

// ── Token 过期测试 ──

describe('Token 过期', () => {
  it('me 返回 401 → 自动 logout、清除状态', async () => {
    localStorage.setItem('access_token', 'expired-token')
    mockFetchOnce({ detail: 'Token expired' }, false)

    renderWithAuth(<TestConsumer />)

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
    })
    expect(screen.getByTestId('token')).toHaveTextContent('null')
  })
})

// ── 初始状态测试 ──

describe('初始状态', () => {
  it('未登录 → loading=false, user=null, isAuthenticated=false', async () => {
    renderWithAuth(<TestConsumer />)

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false')
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false')
      expect(screen.getByTestId('user')).toHaveTextContent('null')
    })
  })
})
