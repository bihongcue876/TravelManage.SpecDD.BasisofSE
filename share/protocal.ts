/**
 * 旅游业务管理系统 - 接口协议定义 v2.2
 * 对应后端 API (FastAPI + SQLAlchemy)
 * 用途: 前端 TypeScript 类型安全 + 路径统一管理
 * 
 * 变更：角色体系由旧四角色调整为三角色（admin / frontdesk / finance）
 */

// ───────────────────── 基础类型 ─────────────────────

export type Role = 'admin' | 'frontdesk' | 'finance';
export type AppState = 'draft' | 'deposit_paid' | 'confirmed' | 'cancelled';
export type PaymentType = 'deposit' | 'balance';
export type PaymentMethod = 'cash' | 'bank_transfer' | 'wechat' | 'alipay';
export type RefundStatus = 'pending' | 'approved' | 'rejected' | 'completed';
export type RefundChannel = 'original' | 'cash' | 'bank_transfer';
export type ReminderType = 'email' | 'sms' | 'print';
export type Gender = 'M' | 'F';
export type DateString = string;     // YYYY-MM-DD
export type DateTimeString = string; // ISO 8601

// ───────────────────── 认证 / 用户 ─────────────────────

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  role: Role;
  username: string;
  name: string;
}

export interface UserInfo {
  id: number;
  username: string;
  name: string;
  role: Role;
  email: string | null;
  phone: string | null;
  is_active: boolean;
  created_at: DateTimeString;
}

export interface UserCreateRequest {
  username: string;
  password: string;
  name: string;
  role: Role;
  email?: string;
  phone?: string;
}

export interface UserUpdateRequest {
  username?: string;
  password?: string;
  name?: string;
  role?: Role;
  email?: string;
  phone?: string;
  is_active?: boolean;
}

export interface ChangePasswordRequest {
  old_password: string;
  new_password: string;
}

// ───────────────────── 工作台（角色化仪表盘）─────────────────────
// 建议后端提供统一 /api/dashboard 接口，根据当前登录用户的角色返回不同数据
export interface DashboardResponse {
  /** 管理员仪表盘 */
  total_users?: number;
  total_applications?: number;
  today_income?: number;
  pending_refunds?: number;
  /** 前台仪表盘 */
  new_applications_today?: number;
  pending_participants?: number;
  /** 财务仪表盘 */
  yesterday_income?: number;
  yesterday_exports?: number;
  pending_approvals?: number;
  // 具体字段以后端实际返回为准
}

// ───────────────────── 路线 ─────────────────────

export interface RouteResponse {
  id: number;
  code: string;
  name: string;
  descr: string | null;
  is_active: boolean;
  created_at: DateTimeString;
}

export interface RouteCreateRequest {
  name: string;
  descr?: string;
  is_active?: boolean;
}

export interface RouteUpdateRequest {
  name?: string;
  descr?: string;
  is_active?: boolean;
}

// ───────────────────── 旅游团 ─────────────────────

export interface GroupResponse {
  id: number;
  route_id: number;
  code: string;
  departure_date: DateString;
  deadline: DateString;
  max_pax: number;
  adult_price: number | null;
  child_price: number | null;
  is_published: boolean;
  created_at: DateTimeString;
}

export interface GroupDetailResponse extends GroupResponse {
  route: RouteResponse;
}

export interface GroupCreateRequest {
  route_id: number;
  code: string;
  departure_date: DateString;
  deadline: DateString;
  max_pax: number;
  adult_price?: number;
  child_price?: number;
}

export interface GroupUpdateRequest {
  code?: string;
  departure_date?: DateString;
  deadline?: DateString;
  max_pax?: number;
  adult_price?: number;
  child_price?: number;
  is_published?: boolean;
}

export interface AvailabilityResponse {
  group_id: number;
  max_pax: number;
  occupied: number;
  available: number;
}

export interface PricingPreviewResponse {
  deposit: number;
  total_price: number;
  deposit_rate: string;
}

export interface BalanceDeadlineResponse {
  balance_deadline: DateString;
  base_deadline: DateString;
  fallback_deadline: DateString;
}

// ───────────────────── 申请单 ─────────────────────

export interface ApplicationResponse {
  id: number;
  group_id: number;
  name: string;
  phone: string;
  email: string | null;
  address: string | null;
  zip_code: string | null;
  adults: number;
  children: number;
  deposit: number;
  total_price: number;
  paid_deposit: number;
  paid_balance: number;
  state: AppState;
  info_completed: boolean;
  cancelled_at: DateTimeString | null;
  created_at: DateTimeString;
}

export interface ApplicationDetailResponse extends ApplicationResponse {
  participants: ParticipantResponse[];
  group: GroupResponse;
}

export interface ApplicationCreateRequest {
  group_id: number;
  name: string;
  phone: string;
  email?: string;
  address?: string;
  zip_code?: string;
  adults: number;
  children: number;
}

export interface ApplicationSearchParams {
  code?: string;
  departure_from?: DateString;
  departure_to?: DateString;
  name?: string;
}

export interface PaymentRequest {
  amount: number;
  payment_method?: string;
  voucher_paths?: string[];
}

export interface DepositPreviewResponse {
  deposit: number;
  total_price: number;
  deposit_rate: string;
  balance_deadline: DateString;
  remaining_balance: number;
}

export interface RemainingBalanceResponse {
  total_price: number;
  paid_deposit: number;
  paid_balance: number;
  remaining: number;
  balance_deadline: DateString;
  days_until_deadline: number;
}

// ───────────────────── 参加者 ─────────────────────

export interface ParticipantResponse {
  id: number;
  application_id: number;
  name: string;
  gender: Gender | null;
  birth_date: DateString | null;
  phone: string | null;
  email: string | null;
  address: string | null;
  is_leader: boolean;
  extra: Record<string, unknown> | null;
  created_at: DateTimeString;
}

export interface ParticipantCreateRequest {
  name: string;
  gender?: Gender;
  birth_date?: DateString;
  phone?: string;
  email?: string;
  address?: string;
  is_leader: boolean;
  extra?: Record<string, unknown>;
}

export interface ParticipantUpdateRequest extends Partial<ParticipantCreateRequest> {}

export interface ParticipantsBulkRequest {
  participants: ParticipantCreateRequest[];
}

export interface ParticipantEditHistoryResponse {
  id: number;
  participant_id: number;
  field_name: string;
  old_value: string | null;
  new_value: string | null;
  edited_by: string;
  created_at: DateTimeString;
}

export interface DuplicateParticipantWarning {
  field: string;
  value: string;
  existing_participant_id: number;
  existing_application_id: number;
  message: string;
}

// ───────────────────── 支付凭证 ─────────────────────

export interface PaymentVoucherResponse {
  id: number;
  payment_log_id: number;
  file_name: string;
  file_path: string;
  file_size: number | null;
  created_at: DateTimeString;
}

export interface PaymentLogDetailResponse {
  id: number;
  application_id: number;
  type: PaymentType;
  amount: number;
  payment_method: string | null;
  voucher_path: string | null;
  created_at: DateTimeString;
  vouchers: PaymentVoucherResponse[];
}

// ───────────────────── 取消与退款 ─────────────────────

export interface CancelPreviewResponse {
  total_paid: number;
  cancel_fee: number;
  refund_amount: number;
  is_partial: boolean;
  participant_count: number;
  per_participant_refund: number | null;
}

export interface RefundDetailResponse {
  id: number;
  application_id: number;
  participant_id: number | null;
  cancel_fee: number;
  refund_amount: number;
  reason: string | null;
  channel: string | null;
  status: RefundStatus;
  approved_by: string | null;
  approved_at: DateTimeString | null;
  refunded_at: DateTimeString;
}

export interface PartialCancelRequest {
  participant_ids: number[];
  reason?: string;
  channel?: string;
}

export interface RefundApprovalRequest {
  approved: boolean;
  approved_by: string;
}

// ───────────────────── 催款与交款单 ─────────────────────

export interface DailyReminderItem {
  app_id: number;
  name: string;
  phone: string;
  tour_code: string;
  departure: DateString;
  total: number;
  paid: number;
  balance: number;
  balance_deadline: DateString;
}

export interface DailyReminderResponse {
  date: DateString;
  items: DailyReminderItem[];
  count: number;
}

export interface ReminderLogResponse {
  id: number;
  application_id: number;
  reminder_type: ReminderType;
  content: string | null;
  sent_at: DateTimeString;
  success: boolean;
}

export interface PaymentOrderResponse {
  id: number;
  application_id: number;
  order_no: string;
  order_type: string;
  created_at: DateTimeString;
}

export interface BatchPrintRequest {
  application_ids: number[];
  doc_type: 'confirmation' | 'payment_order';
}

export interface BatchPrintResponse {
  documents: Record<string, unknown>[];
  total_count: number;
}

// ───────────────────── 财务 ─────────────────────

export interface FinanceExportRequest {
  target_date?: DateString;
  format?: 'csv' | 'excel' | 'json';
  fields?: string[];
}

export interface FinanceExportResponse {
  export_id: number;
  file_path: string;
  file_format: string;
  record_count: number;
}

export interface FinanceReportResponse {
  period: string;
  total_deposits: number;
  total_balances: number;
  total_refunds: number;
  net_income: number;
  record_count: number;
}

export interface BankReconciliationResponse {
  id: number;
  import_date: DateString;
  file_name: string;
  total_records: number;
  matched_count: number;
  unmatched_count: number;
  created_at: DateTimeString;
}

export interface BankReconciliationItemResponse {
  id: number;
  reconciliation_id: number;
  bank_date: DateString | null;
  bank_amount: number;
  bank_ref: string | null;
  matched_payment_id: number | null;
  is_matched: boolean;
}

// ───────────────────── 端点路径常量 ─────────────────────

export const ENDPOINTS = {
  // ---- 认证 ----
  LOGIN: '/api/auth/login',
  ME: '/api/auth/me',
  CHANGE_PASSWORD: '/api/auth/change-password',

  // ---- 用户管理（管理员专用） ----
  USERS: '/api/users',
  USER: (id: number) => `/api/users/${id}`,

  // ---- 工作台（统一接口，后端按角色返回不同数据） ----
  DASHBOARD: '/api/dashboard',

  // ---- 路线 ----
  LIST_ROUTES: '/api/routes',
  SEARCH_ROUTES: '/api/routes/search',
  GET_ROUTE: (id: number) => `/api/routes/${id}`,
  CREATE_ROUTE: '/api/routes',
  UPDATE_ROUTE: (id: number) => `/api/routes/${id}`,
  DELETE_ROUTE: (id: number) => `/api/routes/${id}`,   // 实际为停用
  DELETE_ROUTE_FORCE: (id: number) => `/api/routes/${id}/force`,  // 硬删除（无关联团时可用）
  IMPORT_ROUTES: '/api/routes/import',
  ROUTE_TEMPLATE: '/api/routes/template',
  BATCH_UPDATE_ROUTES: '/api/routes/batch',

  // ---- 旅游团 ----
  LIST_GROUPS: '/api/groups',
  GET_GROUP: (id: number) => `/api/groups/${id}`,
  CREATE_GROUP: '/api/groups',
  UPDATE_GROUP: (id: number) => `/api/groups/${id}`,
  PUBLISH_GROUP: (id: number) => `/api/groups/${id}/publish`,
  IMPORT_GROUPS: '/api/groups/import',
  GROUP_TEMPLATE: '/api/groups/template',
  GROUP_AVAILABILITY: (id: number) => `/api/groups/${id}/availability`,
  GROUP_PRICING_PREVIEW: (id: number) => `/api/groups/${id}/pricing-preview`,
  GROUP_BALANCE_DEADLINE: (id: number) => `/api/groups/${id}/balance-deadline`,

  // ---- 申请 ----
  CREATE_APPLICATION: '/api/applications',
  GET_APPLICATION: (id: number) => `/api/applications/${id}`,
  SEARCH_APPLICATIONS: '/api/applications/search',
  PAY_DEPOSIT: (id: number) => `/api/applications/${id}/pay-deposit`,
  PAY_BALANCE: (id: number) => `/api/applications/${id}/pay-balance`,
  CANCEL_APPLICATION: (id: number) => `/api/applications/${id}/cancel`,
  PARTIAL_CANCEL: (id: number) => `/api/applications/${id}/partial-cancel`,
  CANCEL_PREVIEW: (id: number) => `/api/applications/${id}/cancel-preview`,
  DEPOSIT_PREVIEW: (id: number) => `/api/applications/${id}/deposit-preview`,
  REMAINING_BALANCE: (id: number) => `/api/applications/${id}/remaining-balance`,
  PAYMENT_LOGS: (id: number) => `/api/applications/${id}/payment-logs`,
  UPLOAD_VOUCHER: (id: number) => `/api/applications/${id}/payment-voucher`,
  REFUNDS: (id: number) => `/api/applications/${id}/refunds`,
  APPROVE_REFUND: (refundId: number) => `/api/applications/refunds/${refundId}/approve`,
  REMINDER_LOGS: (id: number) => `/api/applications/${id}/reminder-logs`,
  GENERATE_ORDER_NO: (id: number) => `/api/applications/${id}/generate-order-no`,
  IMPORT_PARTICIPANTS: (id: number) => `/api/applications/${id}/participants/import`,
  PARTICIPANT_TEMPLATE: '/api/applications/participants/template',
  UPDATE_PARTICIPANT: (participantId: number) => `/api/applications/participants/${participantId}`,
  PARTICIPANT_EDIT_HISTORY: (participantId: number) => `/api/applications/participants/${participantId}/edit-history`,
  DUPLICATE_CHECK: (appId: number) => `/api/applications/${appId}/duplicate-check`,
  ADD_PARTICIPANTS: (id: number) => `/api/applications/${id}/participants`,
  LIST_PARTICIPANTS: (id: number) => `/api/applications/${id}/participants`,

  // ---- 任务 ----
  DAILY_REMINDERS: '/api/tasks/daily-reminders',
  DAILY_FINANCE: '/api/tasks/daily-finance',
  EXPORT_FINANCE: '/api/tasks/daily-finance/export',
  FINANCE_REPORT: '/api/tasks/finance-report',
  BATCH_PRINT: '/api/tasks/batch-print',
  SEND_REMINDER: '/api/tasks/send-reminder',
  TASK_REMINDER_LOGS: '/api/tasks/reminder-logs',
  BANK_RECONCILIATION_IMPORT: '/api/tasks/bank-reconciliation/import',
  BANK_RECONCILIATION: (id: number) => `/api/tasks/bank-reconciliation/${id}`,
  BANK_RECONCILIATION_ITEMS: (id: number) => `/api/tasks/bank-reconciliation/${id}/items`,
} as const;