import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { AlertCircle, CheckCircle2, LogIn } from 'lucide-react'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { useAuth } from '../features/auth/AuthContext'
import { resolveRedirectPath } from '../features/auth/redirectPath'

export function LoginPage() {
  const { signIn, isConfigured, configError } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const confirmed = new URLSearchParams(location.search).get('confirmed') === '1'

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setInfo(null)

    const trimmedEmail = email.trim()
    if (!trimmedEmail) return setError('Please enter your email address.')
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) return setError('Please enter a valid email address.')
    if (!password) return setError('Please enter your password.')
    if (!isConfigured) return setError(configError ?? 'Supabase is not configured.')

    setSubmitting(true)
    const result = await signIn(trimmedEmail, password)
    setSubmitting(false)

    if (result.error) {
      setError(result.error)
      return
    }
    setInfo('Login successful. Redirecting…')
    const from = (location.state as { from?: unknown } | null)?.from
    navigate(resolveRedirectPath(from), { replace: true })
  }

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto grid max-w-5xl items-stretch gap-8 lg:grid-cols-[1fr_1.05fr]">
          <div className="flex flex-col justify-center">
            <p className="eyebrow">Customer account</p>
            <h1 className="mt-3 text-4xl md:text-5xl">Welcome back to CookKart</h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-forest/80">
              Sign in to access your kitchen space and continue your grocery and recipe journey. Your session will stay active across visits on this device.
            </p>
            <div className="mt-8 card-surface bg-forest p-6 text-cream">
              <p className="font-display text-2xl text-cream">A calm place to plan and cook</p>
              <p className="mt-2 text-sm leading-relaxed text-cream/75">
                Authentication is powered by Supabase Auth. Authorized administrators can open the Admin console from the header after signing in.
              </p>
            </div>
          </div>

          <Card className="p-6 md:p-8">
            <div className="mb-6 flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-sage-muted text-forest">
                <LogIn size={20} aria-hidden="true" />
              </span>
              <div>
                <h2 className="text-2xl">Log in</h2>
                <p className="text-sm text-forest/70">Use your email and password</p>
              </div>
            </div>

            {confirmed ? (
              <div className="mb-4 flex items-start gap-3 rounded-2xl bg-sage-muted/50 p-4 text-sm text-forest-dark ring-1 ring-forest/10">
                <CheckCircle2 size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
                <p>Email confirmed. You can log in to your CookKart account.</p>
              </div>
            ) : null}

            {!isConfigured ? (
              <div className="mb-4 flex items-start gap-3 rounded-2xl bg-[#fff4e8] p-4 text-sm text-[#6b3a10] ring-1 ring-[#e7c9a8]" role="alert">
                <AlertCircle size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
                <div>
                  <p className="font-semibold">Configuration required</p>
                  <p className="mt-1">{configError}</p>
                </div>
              </div>
            ) : null}

            {error ? (
              <div className="mb-4 flex items-start gap-3 rounded-2xl bg-red-50 p-4 text-sm text-red-800 ring-1 ring-red-200" role="alert">
                <AlertCircle size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
                <p>{error}</p>
              </div>
            ) : null}

            {info ? (
              <div className="mb-4 flex items-start gap-3 rounded-2xl bg-sage-muted/50 p-4 text-sm text-forest-dark ring-1 ring-forest/10" role="status">
                <CheckCircle2 size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
                <p>{info}</p>
              </div>
            ) : null}

            <form onSubmit={onSubmit} className="space-y-4" noValidate>
              <div>
                <label htmlFor="login-email" className="mb-1.5 block text-sm font-semibold text-forest-dark">Email address</label>
                <input
                  id="login-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-2xl border border-forest/15 bg-white px-4 py-3 text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0"
                  placeholder="you@example.com"
                  required
                />
              </div>
              <div>
                <label htmlFor="login-password" className="mb-1.5 block text-sm font-semibold text-forest-dark">Password</label>
                <input
                  id="login-password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-2xl border border-forest/15 bg-white px-4 py-3 text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0"
                  placeholder="Enter your password"
                  required
                />
              </div>
              <Button type="submit" variant="primary" size="lg" className="w-full" disabled={submitting || !isConfigured}>
                {submitting ? 'Logging in…' : 'Log in'}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-forest/75">
              New to CookKart?{' '}
              <Link to="/signup" className="font-semibold text-forest underline decoration-lime/70 underline-offset-4 hover:text-forest-dark">
                Create an account
              </Link>
            </p>
          </Card>
        </div>
      </div>
    </section>
  )
}
