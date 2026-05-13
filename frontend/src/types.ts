export interface Route {
  id: number
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
  created_at: string
}

export interface CancelPreview {
  total_paid: number
  cancel_fee: number
  refund_amount: number
}

export interface PricingPreview {
  deposit: number
  total_price: number
  deposit_rate: string
}

export interface BalanceDeadline {
  balance_deadline: string
  base_deadline: string
  fallback_deadline: string
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
