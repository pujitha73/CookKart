import type { ButtonHTMLAttributes, ReactNode } from 'react'
import { Link, type LinkProps } from 'react-router-dom'

type Variant = 'primary' | 'secondary' | 'ghost'
type Size = 'md' | 'lg'

const base =
  'inline-flex items-center justify-center gap-2 rounded-full font-semibold transition-all duration-200 focus-visible:outline-none disabled:cursor-not-allowed disabled:opacity-60'

const variants: Record<Variant, string> = {
  primary:
    'bg-forest text-cream hover:bg-forest-dark hover:shadow-[var(--shadow-lift)] hover:-translate-y-0.5',
  secondary:
    'bg-lime text-forest-dark hover:bg-[#b8de52] hover:shadow-[var(--shadow-soft)] hover:-translate-y-0.5',
  ghost:
    'bg-white/60 text-forest ring-1 ring-forest/15 hover:bg-white hover:ring-forest/25',
}

const sizes: Record<Size, string> = {
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-7 py-3.5 text-base',
}

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant
  size?: Size
}

export function Button({ variant = 'primary', size = 'md', className = '', ...props }: ButtonProps) {
  return <button className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props} />
}

type ButtonLinkProps = LinkProps & {
  variant?: Variant
  size?: Size
  children: ReactNode
  className?: string
}

export function ButtonLink({ variant = 'primary', size = 'md', className = '', children, ...props }: ButtonLinkProps) {
  return (
    <Link className={`${base} ${variants[variant]} ${sizes[size]} ${className}`} {...props}>
      {children}
    </Link>
  )
}
