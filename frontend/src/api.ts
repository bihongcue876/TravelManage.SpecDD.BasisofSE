import axios from 'axios'
import type {
  Route, Group, GroupDetail, Application, ApplicationDetail,
  Participant, ParticipantCreate, CancelPreview, PricingPreview,
  DepositPreview, BalanceDeadline, DailyReminder, Availability,
  RemainingBalance, PaymentLogDetail, ParticipantEditHistory,
  DuplicateParticipantWarning, RefundDetail, ReminderLog,
  PaymentOrder, FinanceReport, BankReconciliation, BankReconciliationItem
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

export const importGroupsExcel = (file: File): Promise<{ imported: number; errors: string[] }> => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/groups/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const downloadGroupTemplate = (): Promise<Blob> =>
  api.get('/groups/template', { responseType: 'blob' })

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

export const importRoutesExcel = (file: File): Promise<{ imported: number }> => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/routes/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const downloadRouteTemplate = (): Promise<Blob> =>
  api.get('/routes/template', { responseType: 'blob' })

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

export const payDeposit = (id: number, data: { amount: number; payment_method?: string; voucher_paths?: string[] }): Promise<Application> =>
  api.post(`/applications/${id}/pay-deposit`, data)

export const payBalance = (id: number, data: { amount: number; payment_method?: string; voucher_paths?: string[] }): Promise<Application> =>
  api.post(`/applications/${id}/pay-balance`, data)

export const addParticipants = (id: number, data: { participants: ParticipantCreate[] }): Promise<Application> =>
  api.post(`/applications/${id}/participants`, data)

export const cancelApplication = (id: number, reason?: string, channel?: string): Promise<Application> =>
  api.post(`/applications/${id}/cancel`, null, { params: { reason, channel } })

export const partialCancelApplication = (id: number, data: { participant_ids: number[]; reason?: string; channel?: string }): Promise<Application> =>
  api.post(`/applications/${id}/partial-cancel`, data)

export const getCancelPreview = (id: number): Promise<CancelPreview> =>
  api.get(`/applications/${id}/cancel-preview`)

export const fetchParticipants = (id: number): Promise<Participant[]> =>
  api.get(`/applications/${id}/participants`)

export const updateParticipant = (id: number, data: Partial<ParticipantCreate>, editedBy?: string): Promise<Participant> =>
  api.put(`/applications/participants/${id}`, data, { params: { edited_by: editedBy } })

export const fetchDepositPreview = (id: number): Promise<DepositPreview> =>
  api.get(`/applications/${id}/deposit-preview`)

export const fetchRemainingBalance = (id: number): Promise<RemainingBalance> =>
  api.get(`/applications/${id}/remaining-balance`)

export const fetchPaymentLogs = (id: number): Promise<PaymentLogDetail[]> =>
  api.get(`/applications/${id}/payment-logs`)

export const uploadPaymentVoucher = (id: number, file: File, paymentLogId?: number): Promise<{ id?: number; file_name: string; file_path: string }> => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/applications/${id}/payment-voucher`, formData, {
    params: { payment_log_id: paymentLogId },
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const getParticipantEditHistory = (participantId: number): Promise<ParticipantEditHistory[]> =>
  api.get(`/applications/participants/${participantId}/edit-history`)

export const checkDuplicateParticipants = (id: number, params?: { phone?: string; id_number?: string }): Promise<DuplicateParticipantWarning[]> =>
  api.get(`/applications/${id}/duplicate-check`, { params })

export const importParticipantsExcel = (id: number, file: File): Promise<{ imported: number; application_id: number }> => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post(`/applications/${id}/participants/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const downloadParticipantTemplate = (): Promise<Blob> =>
  api.get('/applications/participants/template', { responseType: 'blob' })

export const fetchRefunds = (id: number): Promise<RefundDetail[]> =>
  api.get(`/applications/${id}/refunds`)

export const approveRefund = (refundId: number, data: { approved: boolean; approved_by: string }): Promise<RefundDetail> =>
  api.put(`/applications/refunds/${refundId}/approve`, data)

export const fetchReminderLogs = (id: number): Promise<ReminderLog[]> =>
  api.get(`/applications/${id}/reminder-logs`)

export const generateOrderNo = (id: number, orderType?: string): Promise<PaymentOrder> =>
  api.post(`/applications/${id}/generate-order-no`, null, { params: { order_type: orderType } })

export const fetchDailyReminders = (params?: { date?: string }): Promise<DailyReminder> =>
  api.get('/tasks/daily-reminders', { params })

export const fetchDailyFinance = (params?: { date?: string; fields?: string }): Promise<Record<string, unknown>[]> =>
  api.get('/tasks/daily-finance', { params })

export const exportDailyFinance = (data: { target_date?: string; format?: string; fields?: string[] }): Promise<{ export_id: number; file_path: string; file_format: string; record_count: number }> =>
  api.post('/tasks/daily-finance/export', data)

export const fetchFinanceReport = (params: { period: string; start_date: string; end_date: string }): Promise<FinanceReport> =>
  api.get('/tasks/finance-report', { params })

export const batchPrintDocuments = (data: { application_ids: number[]; doc_type: string }): Promise<{ documents: Record<string, unknown>[]; total_count: number }> =>
  api.post('/tasks/batch-print', data)

export const sendReminder = (params: { application_id: number; reminder_type: string }): Promise<{ id: number; reminder_type: string; sent_at: string }> =>
  api.post('/tasks/send-reminder', null, { params })

export const fetchTaskReminderLogs = (params?: { application_id?: number; date?: string }): Promise<ReminderLog[]> =>
  api.get('/tasks/reminder-logs', { params })

export const importBankReconciliation = (file: File): Promise<BankReconciliation> => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/tasks/bank-reconciliation/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const fetchBankReconciliation = (id: number): Promise<BankReconciliation> =>
  api.get(`/tasks/bank-reconciliation/${id}`)

export const fetchBankReconciliationItems = (id: number): Promise<BankReconciliationItem[]> =>
  api.get(`/tasks/bank-reconciliation/${id}/items`)
