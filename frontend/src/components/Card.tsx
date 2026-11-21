import type { ReactNode } from 'react'

type CardProps = {
  children: ReactNode
  className?: string
}

export function Card({ children, className = '' }: CardProps) {
  return <div className={`card-surface ${className}`}>{children}</div>
}

type FeatureCardProps = {
  icon?: ReactNode
  eyebrow?: string
  title: string
  description: string
  badge?: string
  className?: string
}

export function FeatureCard({ icon, eyebrow, title, description, badge, className = '' }: FeatureCardProps) {
  return (
    <Card className={`group p-6 md:p-7 transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-lift)] ${className}`}>
      <div className="flex items-start justify-between gap-4">
        {icon ? (
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-sage-muted text-forest ring-1 ring-forest/10">
            {icon}
          </div>
        ) : null}
        {badge ? (
          <span className="rounded-full bg-lime/40 px-3 py-1 text-xs font-semibold text-forest-dark ring-1 ring-lime/60">
            {badge}
          </span>
        ) : null}
      </div>
      {eyebrow ? <p className="eyebrow mt-5">{eyebrow}</p> : null}
      <h3 className="mt-2 text-xl md:text-2xl">{title}</h3>
      <p className="mt-3 text-base leading-relaxed text-forest/80">{description}</p>
    </Card>
  )
}
