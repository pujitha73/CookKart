const statusStyles: Record<string, string> = {
  placed: 'bg-[#fff4e8] text-[#6b3a10] ring-[#e7c9a8]',
  confirmed: 'bg-sage-muted text-forest-dark ring-forest/15',
  cancelled: 'bg-red-50 text-red-800 ring-red-200',
}

export function OrderStatusBadge({ status, label }: { status: string; label?: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ${
        statusStyles[status] ?? 'bg-white text-forest ring-forest/15'
      }`}
    >
      {label ?? status}
    </span>
  )
}

export function AvailabilityBadge({ available }: { available: boolean }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ring-1 ${
        available
          ? 'bg-sage-muted text-forest-dark ring-forest/15'
          : 'bg-red-50 text-red-800 ring-red-200'
      }`}
    >
      {available ? 'Available' : 'Unavailable'}
    </span>
  )
}
