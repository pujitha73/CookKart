import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { AdminForbiddenError, fetchAdminMe } from '../../services/adminApi'
import { useAuth } from '../auth/AuthContext'

type AdminAccessValue = {
  isAdmin: boolean
  isLoading: boolean
  error: string | null
}

const AdminAccessContext = createContext<AdminAccessValue | undefined>(undefined)

/**
 * Administrator access is decided by the backend from the database on every
 * check. No JWT metadata or frontend-supplied role is ever consulted here.
 */
export function AdminAccessProvider({ children }: { children: ReactNode }) {
  const { user, isLoading: authLoading } = useAuth()
  const [isAdmin, setIsAdmin] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    if (authLoading) return () => { active = false }

    if (!user) {
      setIsAdmin(false)
      setIsLoading(false)
      setError(null)
      return () => { active = false }
    }

    setIsLoading(true)
    setError(null)
    fetchAdminMe()
      .then((me) => {
        if (active) setIsAdmin(me.is_admin === true)
      })
      .catch((cause: unknown) => {
        if (!active) return
        setIsAdmin(false)
        setError(
          cause instanceof AdminForbiddenError
            ? null
            : cause instanceof Error
              ? cause.message
              : 'Unable to verify administrator access.',
        )
      })
      .finally(() => {
        if (active) setIsLoading(false)
      })

    return () => { active = false }
  }, [user, authLoading])

  const value = useMemo<AdminAccessValue>(
    () => ({ isAdmin, isLoading, error }),
    [isAdmin, isLoading, error],
  )

  return <AdminAccessContext.Provider value={value}>{children}</AdminAccessContext.Provider>
}

export function useAdminAccess(): AdminAccessValue {
  const ctx = useContext(AdminAccessContext)
  if (!ctx) throw new Error('useAdminAccess must be used within AdminAccessProvider')
  return ctx
}
