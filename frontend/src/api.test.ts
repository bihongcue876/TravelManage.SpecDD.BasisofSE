import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'

// ── 用 vi.hoisted 在 mock 工厂之前初始化 ──
const { mockRequestInterceptor, mockResponseInterceptor, mockAxiosInstance } = vi.hoisted(() => {
  const requestHandlers: { fulfilled: any; rejected?: any }[] = []
  const responseHandlers: { fulfilled: any; rejected?: any }[] = []

  const makeInterceptor = () => {
    const handlers: { fulfilled: any; rejected?: any }[] = []
    return {
      handlers,
      use: vi.fn((fulfilled: any, rejected?: any) => {
        handlers.push({ fulfilled, rejected })
        return handlers.length - 1
      }),
      eject: vi.fn(),
    }
  }

  const reqInt = makeInterceptor()
  const resInt = makeInterceptor()

  return {
    mockRequestInterceptor: reqInt,
    mockResponseInterceptor: resInt,
    mockAxiosInstance: {
      interceptors: {
        request: reqInt,
        response: resInt,
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
    },
  }
})

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
  create: vi.fn(() => mockAxiosInstance),
}))

// ── 模拟 localStorage ──
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: vi.fn((key: string) => store[key] ?? null),
    setItem: vi.fn((key: string, value: string) => { store[key] = value }),
    removeItem: vi.fn((key: string) => { delete store[key] }),
    clear: () => { store = {} },
  }
})()

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock })

const dispatchEvent = vi.fn()
Object.defineProperty(window, 'dispatchEvent', { value: dispatchEvent })

beforeEach(() => {
  localStorageMock.clear()
  vi.clearAllMocks()
})

describe('api.ts interceptors', () => {
  describe('请求拦截器 — 自动带 token', () => {
    it('localStorage 有 token → Authorization header 正确', async () => {
      await import('./api')

      const { fulfilled } = mockRequestInterceptor.handlers[0]
      localStorageMock.setItem('access_token', 'my-token')

      const config = { headers: {} }
      const result = fulfilled(config)
      expect(result.headers.Authorization).toBe('Bearer my-token')
    })

    it('localStorage 无 token → 无 Bearer header', async () => {
      await import('./api')
      const { fulfilled } = mockRequestInterceptor.handlers[0]

      const config = { headers: {} }
      const result = fulfilled(config)
      expect(result.headers.Authorization).toBeUndefined()
    })
  })

  describe('响应拦截器 — 成功响应', () => {
    it('成功响应 → 返回 response.data', async () => {
      await import('./api')
      const { fulfilled } = mockResponseInterceptor.handlers[0]

      const response = { data: { id: 1, name: 'test' } }
      const result = fulfilled(response)
      expect(result).toEqual({ id: 1, name: 'test' })
    })
  })

  describe('响应拦截器 — 401 错误处理', () => {
    it('非登录接口 401 → 清除 token、触发 auth:logout 事件', async () => {
      await import('./api')
      const { rejected } = mockResponseInterceptor.handlers[0]

      localStorageMock.setItem('access_token', 'some-token')
      const error = {
        response: { status: 401 },
        config: { url: '/api/groups' },
      }

      await expect(() => rejected(error)).rejects.toThrow()
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
      expect(dispatchEvent).toHaveBeenCalled()
    })

    it('登录接口 401 → 不清除 token', async () => {
      await import('./api')
      const { rejected } = mockResponseInterceptor.handlers[0]

      localStorageMock.setItem('access_token', 'some-token')
      const error = {
        response: { status: 401 },
        config: { url: '/api/auth/login' },
      }

      await expect(() => rejected(error)).rejects.toThrow()
      // 登录接口即使 401 也不清除 token
      expect(localStorageMock.removeItem).not.toHaveBeenCalled()
    })

    it('401 错误信息从 response.data.detail 提取', async () => {
      await import('./api')
      const { rejected } = mockResponseInterceptor.handlers[0]

      const error = {
        response: { status: 401, data: { detail: 'Token expired' } },
        config: { url: '/api/groups' },
      }

      await expect(() => rejected(error)).rejects.toThrow('Token expired')
    })
  })
})
