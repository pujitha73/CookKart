/** Resolve a `from` location (string path or React Router location object) to a safe local path. */
export function resolveRedirectPath(from: unknown): string {
  if (typeof from === 'string' && from.startsWith('/') && !from.startsWith('//')) return from
  if (from && typeof from === 'object') {
    const loc = from as { pathname?: string; search?: string; hash?: string }
    if (
      typeof loc.pathname === 'string' &&
      loc.pathname.startsWith('/') &&
      !loc.pathname.startsWith('//')
    ) {
      return `${loc.pathname}${loc.search || ''}${loc.hash || ''}`
    }
  }
  return '/'
}
