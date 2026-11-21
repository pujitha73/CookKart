import { useState } from 'react'

type Props = {
  src?: string | null
  alt: string
  className?: string
  priority?: boolean
  sizes?: string
}

export function ExternalImage({ src, alt, className = '', priority = false, sizes }: Props) {
  const [failed, setFailed] = useState(false)

  if (failed || !src) {
    return (
      <div
        className={`flex items-center justify-center bg-gradient-to-br from-sage-muted via-cream to-cream-deep text-forest ${className}`}
        role="img"
        aria-label={alt}
      >
        <div className="px-4 text-center">
          <p className="font-display text-lg">CookKart</p>
          <p className="mt-1 text-sm text-forest/70">Image preview unavailable</p>
        </div>
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      loading={priority ? 'eager' : 'lazy'}
      fetchPriority={priority ? 'high' : 'auto'}
      decoding="async"
      sizes={sizes}
      onError={() => setFailed(true)}
    />
  )
}
