import dayjs from 'dayjs'

export interface DepositResult {
  rate: number
  rateLabel: string
  deposit: number
}

export interface CancellationFeeResult {
  rate: number
  rateLabel: string
  fee: number
  refund: number
}

export interface BalanceDueDateResult {
  balanceDueDate: string
  baseDeadline: string
  fallbackDeadline: string
  adjusted: boolean
}

function isValidDate(date: unknown): date is string {
  if (typeof date !== 'string' || date.trim() === '') return false
  return dayjs(date).isValid()
}

export function daysUntilDeparture(departureDate: string, referenceDate?: string): number {
  if (!isValidDate(departureDate)) {
    throw new TypeError('出发日期无效')
  }
  const ref = referenceDate && isValidDate(referenceDate) ? dayjs(referenceDate) : dayjs()
  const departure = dayjs(departureDate).startOf('day')
  return departure.diff(ref.startOf('day'), 'day')
}

export function calculateDeposit(departureDate: string, totalPrice: number, referenceDate?: string): DepositResult {
  if (!isValidDate(departureDate)) {
    throw new TypeError('出发日期无效')
  }
  if (totalPrice <= 0) {
    throw new RangeError('总金额必须大于0')
  }

  const daysDiff = daysUntilDeparture(departureDate, referenceDate)

  let rate: number
  let rateLabel: string

  if (daysDiff >= 60) {
    rate = 0.10
    rateLabel = '10%'
  } else if (daysDiff >= 30) {
    rate = 0.20
    rateLabel = '20%'
  } else {
    rate = 1.0
    rateLabel = '100%'
  }

  const deposit = Math.round(totalPrice * rate * 100) / 100

  return { rate, rateLabel, deposit }
}

export function calculateCancellationFee(departureDate: string, paidAmount: number, referenceDate?: string): CancellationFeeResult {
  if (!isValidDate(departureDate)) {
    throw new TypeError('出发日期无效')
  }

  if (paidAmount <= 0) {
    return { rate: 0, rateLabel: '0%', fee: 0, refund: 0 }
  }

  const daysDiff = daysUntilDeparture(departureDate, referenceDate)

  let rate: number
  let rateLabel: string

  if (daysDiff < 0) {
    rate = 1.0
    rateLabel = '100%'
  } else if (daysDiff <= 9) {
    rate = 0.50
    rateLabel = '50%'
  } else if (daysDiff <= 29) {
    rate = 0.20
    rateLabel = '20%'
  } else {
    rate = 0
    rateLabel = '0%'
  }

  const fee = Math.round(paidAmount * rate * 100) / 100
  const refund = Math.round((paidAmount - fee) * 100) / 100

  return { rate, rateLabel, fee, refund }
}

export function calculateBalanceDueDate(departureDate: string, slipSendDate?: string | null): BalanceDueDateResult {
  if (!isValidDate(departureDate)) {
    throw new TypeError('出发日期无效')
  }

  const departure = dayjs(departureDate).startOf('day')
  const baseDeadline = departure.subtract(30, 'day').format('YYYY-MM-DD')

  if (!slipSendDate || !isValidDate(slipSendDate)) {
    return {
      balanceDueDate: baseDeadline,
      baseDeadline,
      fallbackDeadline: baseDeadline,
      adjusted: false,
    }
  }

  const slipDate = dayjs(slipSendDate).startOf('day')
  const baseDeadlineDate = dayjs(baseDeadline).startOf('day')
  const daysFromSlipToBase = baseDeadlineDate.diff(slipDate, 'day')

  if (daysFromSlipToBase < 10) {
    const fallbackDeadline = slipDate.add(10, 'day').format('YYYY-MM-DD')
    return {
      balanceDueDate: fallbackDeadline,
      baseDeadline,
      fallbackDeadline,
      adjusted: true,
    }
  }

  return {
    balanceDueDate: baseDeadline,
    baseDeadline,
    fallbackDeadline: baseDeadline,
    adjusted: false,
  }
}