import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, CheckCircle2, UserPlus } from 'lucide-react'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { useAuth } from '../features/auth/AuthContext'

export function SignupPage() {
  const { signUp, isConfigured, configError } = useAuth()
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function onSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    const name = fullName.trim()
    const trimmedEmail = email.trim()
    if (!name) return setError('Please enter your full name.')
    if (name.length < 2) return setError('Full name must be at least 2 characters.')
    if (!trimmedEmail) return setError('Please enter your email address.')
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) return setError('Please enter a valid email address.')
    if (!password) return setError('Please create a password.')
    if (password.length < 6) return setError('Password must be at least 6 characters.')
    if (password !== confirmPassword) return setError('Passwords do not match.')
    if (!isConfigured) return setError(configError ?? 'Supabase is not configured.')

    setSubmitting(true)
    const result = await signUp(trimmedEmail, password, name)
    setSubmitting(false)

    if (result.error) {
      setError(result.error)
      return
    }

    if (result.needsEmailConfirmation) {
      setSuccess('Account created. Please check your email to confirm your address before logging in.')
      setPassword('')
      setConfirmPassword('')
      return
    }

    setSuccess('Account created successfully. Redirecting to the homepage…')
    navigate('/', { replace: true })
  }

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto grid max-w-5xl items-stretch gap-8 lg:grid-cols-[1fr_1.05fr]">
          <div className="flex flex-col justify-center">
            <p className="eyebrow">Join CookKart</p>
            <h1 className="mt-3 text-4xl md:text-5xl">Create your customer account</h1>
            <p className="mt-5 max-w-xl text-lg leading-relaxed text-forest/80">
              Set up your CookKart account to personalize your kitchen experience. We’ll store your name securely in your Supabase profile metadata.
            </p>
            <ul className="mt-8 space-y-3 text-forest/80">
              <li className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-lime" aria-hidden="true" /><span>Access your customer-only kitchen space.</span></li>
              <li className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-lime" aria-hidden="true" /><span>Keep your session signed in across refreshes.</span></li>
              <li className="flex gap-3"><span className="mt-1 h-2.5 w-2.5 rounded-full bg-lime" aria-hidden="true" /><span>Email confirmation is supported when enabled in Supabase.</span></li>
            </ul>
          </div>

          <Card className="p-6 md:p-8">
            <div className="mb-6 flex items-center gap-3">
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-sage-muted text-forest">
                <UserPlus size={20} aria-hidden="true" />
              </span>
              <div>
                <h2 className="text-2xl">Sign up</h2>
                <p className="text-sm text-forest/70">Create your CookKart account</p>
              </div>
            </div>

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

            {success ? (
              <div className="mb-4 flex items-start gap-3 rounded-2xl bg-sage-muted/50 p-4 text-sm text-forest-dark ring-1 ring-forest/10" role="status">
                <CheckCircle2 size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
                <p>{success}</p>
              </div>
            ) : null}

            <form onSubmit={onSubmit} className="space-y-4" noValidate>
              <div>
                <label htmlFor="signup-name" className="mb-1.5 block text-sm font-semibold text-forest-dark">Full name</label>
                <input
                  id="signup-name"
                  name="fullName"
                  type="text"
                  autoComplete="name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-2xl border border-forest/15 bg-white px-4 py-3 text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0"
                  placeholder="Your full name"
                  required
                />
              </div>
              <div>
                <label htmlFor="signup-email" className="mb-1.5 block text-sm font-semibold text-forest-dark">Email address</label>
                <input
                  id="signup-email"
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
                <label htmlFor="signup-password" className="mb-1.5 block text-sm font-semibold text-forest-dark">Password</label>
                <input
                  id="signup-password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-2xl border border-forest/15 bg-white px-4 py-3 text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0"
                  placeholder="At least 6 characters"
                  required
                />
              </div>
              <div>
                <label htmlFor="signup-confirm" className="mb-1.5 block text-sm font-semibold text-forest-dark">Confirm password</label>
                <input
                  id="signup-confirm"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-2xl border border-forest/15 bg-white px-4 py-3 text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0"
                  placeholder="Re-enter your password"
                  required
                />
              </div>
              <Button type="submit" variant="primary" size="lg" className="w-full" disabled={submitting || !isConfigured}>
                {submitting ? 'Creating account…' : 'Create account'}
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-forest/75">
              Already have an account?{' '}
              <Link to="/login" className="font-semibold text-forest underline decoration-lime/70 underline-offset-4 hover:text-forest-dark">
                Log in
              </Link>
            </p>
          </Card>
        </div>
      </div>
    </section>
  )
}
