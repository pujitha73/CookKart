import { AlertCircle } from 'lucide-react'
import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { useAdminAccess } from './AdminAccessContext'

function AdminLoading() {
  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-md card-surface p-8 text-center">
          <p className="eyebrow">Admin console</p>
          <p className="mt-3 text-lg text-forest/80">Verifying administrator access…</p>
        </div>
      </div>
    </section>
  )
}

/** Route guard backed by the server-side admin check, not client-side roles. */
export function AdminRoute() {
  const { user, isLoading: authLoading } = useAuth()
  const { isAdmin, isLoading: adminLoading, error } = useAdminAccess()
  const location = useLocation()

  if (authLoading || adminLoading) return <AdminLoading />

  if (error) {
    return (
      <section className="section-space">
        <div className="container-page">
          <div className="mx-auto max-w-lg card-surface p-8" role="alert">
            <div className="flex items-start gap-3">
              <AlertCircle className="mt-0.5 shrink-0 text-forest" aria-hidden="true" />
              <div>
                <p className="font-display text-2xl">Admin console unavailable</p>
                <p className="mt-2 text-sm text-forest/80">{error}</p>
                <p className="mt-2 text-sm text-forest/70">Please refresh the page and try again.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (!user) return <Navigate to="/login" replace state={{ from: location }} />
  if (!isAdmin) return <Navigate to="/" replace />

  return <Outlet />
}
