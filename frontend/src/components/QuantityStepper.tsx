import { Minus, Plus } from 'lucide-react'

export const MAX_QUANTITY = 99

type Props = {
  value: number
  onChange: (next: number) => void
  label: string
  disabled?: boolean
  min?: number
  max?: number
  compact?: boolean
}

export function QuantityStepper({
  value,
  onChange,
  label,
  disabled = false,
  min = 1,
  max = MAX_QUANTITY,
  compact = false,
}: Props) {
  const size = compact ? 'h-8 w-8' : 'h-9 w-9'

  return (
    <div className="inline-flex items-center rounded-full ring-1 ring-forest/15">
      <button
        type="button"
        className={`inline-flex ${size} items-center justify-center rounded-l-full text-forest transition hover:bg-sage-muted/60 disabled:cursor-not-allowed disabled:opacity-40`}
        aria-label={`Decrease quantity of ${label}`}
        disabled={disabled || value <= min}
        onClick={() => onChange(value - 1)}
      >
        <Minus size={15} aria-hidden="true" />
      </button>
      <span className="w-9 text-center text-sm font-bold text-forest-dark" aria-live="polite">
        {value}
      </span>
      <button
        type="button"
        className={`inline-flex ${size} items-center justify-center rounded-r-full text-forest transition hover:bg-sage-muted/60 disabled:cursor-not-allowed disabled:opacity-40`}
        aria-label={`Increase quantity of ${label}`}
        disabled={disabled || value >= max}
        onClick={() => onChange(value + 1)}
      >
        <Plus size={15} aria-hidden="true" />
      </button>
    </div>
  )
}
