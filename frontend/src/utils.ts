import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

/** 格式化为中文日期时间：2026年6月7日 14:30 */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return '-'
  return dayjs(iso).format('YYYY年M月D日 HH:mm')
}

/** 格式化为中文日期：2026年6月7日 */
export function formatDate(iso: string | null | undefined): string {
  if (!iso) return '-'
  return dayjs(iso).format('YYYY年M月D日')
}

/** 格式化为中文月日：6月7日 */
export function formatMonthDay(iso: string | null | undefined): string {
  if (!iso) return '-'
  return dayjs(iso).format('M月D日')
}

/** 格式化为中文星期：星期一、星期二 ... */
export function formatWeekday(iso: string | null | undefined): string {
  if (!iso) return '-'
  const weekMap = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
  return weekMap[dayjs(iso).day()]
}
