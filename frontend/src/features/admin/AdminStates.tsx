import { AlertCircle, CheckCircle2, Inbox } from 'lucide-react'
import { Button } from '../../components/Button'

export function AdminLoading({ label = 'Loading records…' }: { label?: string }) {
  return (
    <div className="card-surface p-10 text-center text-forest/75" role="status">
      {label}
    </div>
  )
}

export function AdminError({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="card-surface p-6" role="alert">
      <div className="flex flex-wrap items-start gap-3">
        <AlertCircle className="mt-0.5 shrink-0 text-forest" aria-hidden="true" />
        <div className="min-w-0 flex-1">
          <p className="font-semibold text-forest-dark">Something went wrong</p>
          <p className="mt-1 break-words text-sm text-forest/80">{message}</p>
          {onRetry ? (
            <Button variant="ghost" size="md" className="mt-4" onClick={onRetry}>
              Try again
            </Button>
          ) : null}
        </div>
      </div>
    </div>
  )
}

export function AdminEmpty({ title, description }: { title: string; description: string }) {
  return (
    <div className="card-surface p-10 text-center">
      <Inbox className="mx-auto text-forest/50" size={28} aria-hidden="true" />
      <p className="mt-3 font-display text-xl text-forest-dark">{title}</p>
      <p className="mt-2 text-sm text-forest/75">{description}</p>
    </div>
  )
}

export function AdminSuccess({ message }: { message: string }) {
  return (
    <div
      className="mb-4 flex items-start gap-3 rounded-2xl bg-sage-muted/60 p-4 text-sm text-forest-dark ring-1 ring-forest/10"
      role="status"
    >
      <CheckCircle2 className="mt-0.5 shrink-0" size={18} aria-hidden="true" />
      <p className="break-words">{message}</p>
    </div>
  )
}

export function errorMessage(cause: unknown): string {
  return cause instanceof Error && cause.message.trim()
    ? cause.message
    : 'The request could not be completed. Please try again.'
}
