export function formatAdminMoney(value: string | number, currency = 'INR'): string {
  const amount = typeof value === 'string' ? Number(value) : value
  if (Number.isNaN(amount)) return String(value)
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: currency || 'INR',
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatAdminDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
}
