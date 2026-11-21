/**
 * Short-lived in-memory cache for public, read-only catalogue requests only.
 *
 * It is deliberately limited to endpoints that need no authentication and
 * expose no private or administrative data. Entries expire quickly so an
 * administrator's catalogue changes become visible without a manual refresh.
 */
type CacheEntry<T> = { value: T; expiresAt: number }

const entries = new Map<string, CacheEntry<unknown>>()
const inFlight = new Map<string, Promise<unknown>>()

const DEFAULT_TTL_MS = 60_000

/** Returns cached data when fresh, otherwise shares a single in-flight request. */
export function cachedRequest<T>(key: string, load: () => Promise<T>, ttlMs = DEFAULT_TTL_MS): Promise<T> {
  const cached = entries.get(key) as CacheEntry<T> | undefined
  if (cached && cached.expiresAt > Date.now()) {
    return Promise.resolve(cached.value)
  }

  const pending = inFlight.get(key) as Promise<T> | undefined
  if (pending) return pending

  const request = load()
    .then((value) => {
      entries.set(key, { value, expiresAt: Date.now() + ttlMs })
      return value
    })
    .finally(() => {
      inFlight.delete(key)
    })

  inFlight.set(key, request)
  return request
}

/** Clears all cached public catalogue data (used after catalogue mutations). */
export function clearRequestCache(): void {
  entries.clear()
}
