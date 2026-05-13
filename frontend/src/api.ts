import axios from 'axios'
import type {
  Route, Group, GroupDetail, Application, ApplicationDetail,
  Participant, ParticipantCreate, CancelPreview, PricingPreview,
  BalanceDeadline, DailyReminder, Availability
} from './types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

export const fetchGroups = (params?: Record<string, string | number>): Promise<Group[]> =>
  api.get('/groups', { params })

export const fetchGroup = (id: number): Promise<GroupDetail> =>
  api.get(`/groups/${id}`)

export const createGroup = (data: Partial<Group>): Promise<Group> =>
  api.post('/groups', data)

export const updateGroup = (id: number, data: Partial<Group>): Promise<Group> =>
  api.put(`/groups/${id}`, data)

export const publishGroup = (id: number): Promise<Group> =>
  api.post(`/groups/${id}/publish`)

export const checkAvailability = (id: number): Promise<Availability> =>
  api.get(`/groups/${id}/availability`)

export const fetchPricingPreview = (id: number, params: { adults: number; children: number }): Promise<PricingPreview> =>
  api.get(`/groups/${id}/pricing-preview`, { params })

export const fetchBalanceDeadline = (id: number, params?: { today?: string }): Promise<BalanceDeadline> =>
  api.get(`/groups/${id}/balance-deadline`, { params })

export const fetchRoutes = (): Promise<Route[]> => api.get('/routes')

export const fetchRoute = (id: number): Promise<Route> => api.get(`/routes/${id}`)

export const createRoute = (data: Partial<Route>): Promise<Route> => api.post('/routes', data)

export const updateRoute = (id: number, data: Partial<Route>): Promise<Route> =>
  api.put(`/routes/${id}`, data)

export const createApplication = (data: {
  group_id: number
  name: string
  phone: string
  email?: string
  address?: string
  zip_code?: string
  adults: number
  children: number
}): Promise<Application> => api.post('/applications', data)

export const fetchApplication = (id: number): Promise<ApplicationDetail> =>
  api.get(`/applications/${id}`)

export const searchApplications = (params?: Record<string, string | number>): Promise<Application[]> =>
  api.get('/applications/search', { params })

export const payDeposit = (id: number, data: { amount: number }): Promise<Application> =>
  api.post(`/applications/${id}/pay-deposit`, data)

export const payBalance = (id: number, data: { amount: number }): Promise<Application> =>
  api.post(`/applications/${id}/pay-balance`, data)

export const addParticipants = (id: number, data: { participants: ParticipantCreate[] }): Promise<Application> =>
  api.post(`/applications/${id}/participants`, data)

export const cancelApplication = (id: number, reason?: string): Promise<Application> =>
  api.post(`/applications/${id}/cancel`, null, { params: { reason } })

export const getCancelPreview = (id: number): Promise<CancelPreview> =>
  api.get(`/applications/${id}/cancel-preview`)

export const fetchParticipants = (id: number): Promise<Participant[]> =>
  api.get(`/applications/${id}/participants`)

export const updateParticipant = (id: number, data: Partial<ParticipantCreate>): Promise<Participant> =>
  api.put(`/applications/participants/${id}`, data)

export const fetchDailyReminders = (params?: { date?: string }): Promise<DailyReminder> =>
  api.get('/tasks/daily-reminders', { params })

export const fetchDailyFinance = (params?: { date?: string }): Promise<Record<string, unknown>[]> =>
  api.get('/tasks/daily-finance', { params })

export const exportDailyFinance = (params?: { target_date?: string }): Promise<{ export_id: number; file_path: string; record_count: number }> =>
  api.post('/tasks/daily-finance/export', null, { params })
