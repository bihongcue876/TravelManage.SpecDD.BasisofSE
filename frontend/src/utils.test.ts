import { describe, it, expect } from 'vitest'
import { formatDateTime, formatDate, formatMonthDay, formatWeekday } from './utils'

describe('formatDateTime', () => {
  it('正常 ISO 日期时间 → "YYYY年M月D日 HH:mm"', () => {
    expect(formatDateTime('2026-06-07T14:30:00')).toBe('2026年6月7日 14:30')
  })

  it('null → "-"', () => {
    expect(formatDateTime(null)).toBe('-')
  })

  it('undefined → "-"', () => {
    expect(formatDateTime(undefined)).toBe('-')
  })
})

describe('formatDate', () => {
  it('正常 ISO 日期 → "YYYY年M月D日"', () => {
    expect(formatDate('2026-06-07T00:00:00')).toBe('2026年6月7日')
  })

  it('null → "-"', () => {
    expect(formatDate(null)).toBe('-')
  })

  it('undefined → "-"', () => {
    expect(formatDate(undefined)).toBe('-')
  })
})

describe('formatMonthDay', () => {
  it('正常日期 → "M月D日"', () => {
    expect(formatMonthDay('2026-06-07')).toBe('6月7日')
  })

  it('null → "-"', () => {
    expect(formatMonthDay(null)).toBe('-')
  })

  it('undefined → "-"', () => {
    expect(formatMonthDay(undefined)).toBe('-')
  })
})

describe('formatWeekday', () => {
  it('2026-06-07（星期日）→ "星期日"', () => {
    expect(formatWeekday('2026-06-07')).toBe('星期日')
  })

  it('2026-06-08（星期一）→ "星期一"', () => {
    expect(formatWeekday('2026-06-08')).toBe('星期一')
  })

  it('null → "-"', () => {
    expect(formatWeekday(null)).toBe('-')
  })

  it('undefined → "-"', () => {
    expect(formatWeekday(undefined)).toBe('-')
  })
})
