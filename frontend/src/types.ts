export interface Route {
  id: number
  code: string
  name: string
  descr: string | null
  is_active: boolean
  created_at: string
}

export interface Group {
  id: number
  route_id: number
  code: string
  departure_date: string
  deadline: string
  max_pax: number
  adult_price: number | null
  child_price: number | null
  is_published: boolean
  created_at: string
}

export interface GroupDetail extends Group {
  route: Route
}

export interface Application {
  id: number
  group_id: number
  name: string
  phone: string
  email: string | null
  address: string | null
  zip_code: string | null
  adults: number
  children: number
  deposit: number
  total_price: number
  paid_deposit: number
  paid_balance: number
  state: 'draft' | 'deposit_paid' | 'confirmed' | 'cancelled'
  info_completed: boolean
  cancelled_at: string | null
  created_at: string
}

export interface ApplicationDetail extends Application {
  participants: Participant[]
  group: Group
}

export interface Participant {
  id: number
  application_id: number
  name: string
  gender: string | null
  birth_date: string | null
  phone: string | null
  email: string | null
  address: string | null
  is_leader: boolean
  extra: Record<string, unknown> | null
  created_at: string
}

export interface ParticipantCreate {
  name: string
  gender?: string
  birth_date?: string
  phone?: string
  email?: string
  address?: string
  is_leader: boolean
  extra?: Record<string, unknown>
}

export interface PaymentLog {
  id: number
  application_id: number
  type: 'deposit' | 'balance'
  amount: number
  payment_method: string | null
  voucher_path: string | null
  created_at: string
}

export interface PaymentVoucher {
  id: number
  payment_log_id: number
  file_name: string
  file_path: string
  file_size: number | null
  created_at: string
}

export interface PaymentLogDetail extends PaymentLog {
  vouchers: PaymentVoucher[]
}

export interface CancelPreview {
  total_paid: number
  cancel_fee: number
  refund_amount: number
  is_partial: boolean
  participant_count: number
  per_participant_refund: number | null
}

export interface PricingPreview {
  deposit: number
  total_price: number
  deposit_rate: string
}

export interface DepositPreview {
  deposit: number
  total_price: number
  deposit_rate: string
  balance_deadline: string
  remaining_balance: number
}

export interface BalanceDeadline {
  balance_deadline: string
  base_deadline: string
  fallback_deadline: string
}

export interface RemainingBalance {
  total_price: number
  paid_deposit: number
  paid_balance: number
  remaining: number
  balance_deadline: string
  days_until_deadline: number
}

export interface DailyReminderItem {
  app_id: number
  name: string
  phone: string
  tour_code: string
  departure: string
  total: number
  paid: number
  balance: number
  balance_deadline: string
}

export interface DailyReminder {
  date: string
  items: DailyReminderItem[]
  count: number
}

export interface Availability {
  group_id: number
  max_pax: number
  occupied: number
  available: number
}

export interface ParticipantEditHistory {
  id: number
  participant_id: number
  field_name: string
  old_value: string | null
  new_value: string | null
  edited_by: string
  created_at: string
}

export interface DuplicateParticipantWarning {
  field: string
  value: string
  existing_participant_id: number
  existing_application_id: number
  message: string
}

export interface RefundDetail {
  id: number
  application_id: number
  participant_id: number | null
  cancel_fee: number
  refund_amount: number
  reason: string | null
  channel: string | null
  status: 'pending' | 'approved' | 'rejected' | 'completed'
  approved_by: string | null
  approved_at: string | null
  refunded_at: string
}

export interface ReminderLog {
  id: number
  application_id: number
  reminder_type: 'email' | 'sms' | 'print'
  content: string | null
  sent_at: string
  success: boolean
}

export interface PaymentOrder {
  id: number
  application_id: number
  order_no: string
  order_type: string
  created_at: string
}

export interface FinanceReport {
  period: string
  total_deposits: number
  total_balances: number
  total_refunds: number
  net_income: number
  record_count: number
}

export interface BankReconciliation {
  id: number
  import_date: string
  file_name: string
  total_records: number
  matched_count: number
  unmatched_count: number
  created_at: string
}

export interface BankReconciliationItem {
  id: number
  reconciliation_id: number
  bank_date: string | null
  bank_amount: number
  bank_ref: string | null
  matched_payment_id: number | null
  is_matched: boolean
}

// ── 用户相关类型 ──

export interface UserInfo {
  id: number
  username: string
  name: string
  role: string
  email: string | null
  phone: string | null
  is_active: boolean
  created_at: string
}

export interface PredefinedUser {
  username: string
  name: string
  role: string
  default_password: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

// ── 类型别名（与 protocal.ts 对齐） ──

export type Gender = 'M' | 'F' | 'O'
export type AppState = 'draft' | 'deposit_paid' | 'confirmed' | 'cancelled'
export type PaymentType = 'deposit' | 'balance'
export type PaymentMethod = 'cash' | 'bank_transfer' | 'wechat' | 'alipay'
export type RefundStatus = 'pending' | 'approved' | 'rejected' | 'completed'
export type RefundChannel = 'original' | 'cash' | 'bank_transfer'
export type ReminderType = 'email' | 'sms' | 'print'

// ── 缺失的请求/响应类型 ──

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  role: string
  username: string
  name: string
}

export interface FrontdeskDashboard {
  new_applications_today: number
  pending_participants: number
}

export interface CollectorDashboard {
  reminders_today: number
  overdue_balance: number
}

export interface ProductDashboard {
  upcoming_groups: number
  unpublished_groups: number
}

export interface FinanceDashboard {
  yesterday_income: number
  yesterday_exports: number
  pending_refunds: number
}

export interface UserCreateRequest {
  username: string
  password: string
  name: string
  role: string
  email?: string
  phone?: string
}

export interface UserUpdateRequest {
  username?: string
  password?: string
  name?: string
  role?: string
  email?: string
  phone?: string
  is_active?: boolean
}

export interface FinanceExportRequest {
  target_date?: string
  format?: 'csv' | 'excel' | 'json'
  fields?: string[]
}

export interface FinanceExportResponse {
  export_id: number
  file_path: string
  file_format: string
  record_count: number
}
