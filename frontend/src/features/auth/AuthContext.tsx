import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { Session, User } from '@supabase/supabase-js'
import { getSupabaseConfigError, isSupabaseConfigured, supabase } from '../../services/supabaseClient'

type AuthResult = { error: string | null; needsEmailConfirmation?: boolean }

type AuthContextValue = {
  user: User | null
  session: Session | null
  isLoading: boolean
  isConfigured: boolean
  configError: string | null
  signUp: (email: string, password: string, fullName: string) => Promise<AuthResult>
  signIn: (email: string, password: string) => Promise<AuthResult>
  signOut: () => Promise<{ error: string | null }>
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const configError = getSupabaseConfigError()

  useEffect(() => {
    if (!isSupabaseConfigured || !supabase) {
      setIsLoading(false)
      return
    }

    let mounted = true
    supabase.auth
      .getSession()
      .then(({ data, error }) => {
        if (!mounted) return
        if (error) {
          // keep app usable; session will remain null
          console.error('Failed to get session', error.message)
        }
        setSession(data.session ?? null)
        setUser(data.session?.user ?? null)
      })
      .finally(() => {
        if (mounted) setIsLoading(false)
      })

    const { data: sub } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      setSession(nextSession)
      setUser(nextSession?.user ?? null)
      setIsLoading(false)
    })

    return () => {
      mounted = false
      sub.subscription.unsubscribe()
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      session,
      isLoading,
      isConfigured: isSupabaseConfigured,
      configError,
      signUp: async (email, password, fullName) => {
        if (!supabase) return { error: configError ?? 'Supabase is not configured.' }
        const emailRedirectTo = `${window.location.origin}/login`
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: { full_name: fullName },
            emailRedirectTo,
          },
        })
        if (error) return { error: error.message }
        const needsEmailConfirmation = !data.session && !!data.user
        return { error: null, needsEmailConfirmation }
      },
      signIn: async (email, password) => {
        if (!supabase) return { error: configError ?? 'Supabase is not configured.' }
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        return { error: error ? error.message : null }
      },
      signOut: async () => {
        if (!supabase) return { error: configError ?? 'Supabase is not configured.' }
        const { error } = await supabase.auth.signOut()
        return { error: error ? error.message : null }
      },
    }),
    [user, session, isLoading, configError],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
