import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './AuthContext'
import { resolveRedirectPath } from './redirectPath'

function LoadingScreen() {
  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-md card-surface p-8 text-center">
          <p className="eyebrow">Account</p>
          <p className="mt-3 text-lg text-forest/80">Checking your session…</p>
        </div>
      </div>
    </section>
  )
}

export function ProtectedRoute() {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) return <LoadingScreen />
  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return <Outlet />
}

export function GuestRoute() {
  const { user, isLoading } = useAuth()
  const location = useLocation()
  if (isLoading) return <LoadingScreen />
  if (user) {
    const from = (location.state as { from?: unknown } | null)?.from
    return <Navigate to={resolveRedirectPath(from)} replace />
  }
  return <Outlet />
}
