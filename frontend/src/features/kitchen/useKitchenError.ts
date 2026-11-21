import { useCallback } from 'react'
import { AuthenticationError } from '../../services/kitchenApi'
import { useAuth } from '../auth/AuthContext'

/** Converts API errors into user-facing messages and clears expired sessions. */
export function useKitchenError() {
  const { signOut } = useAuth()

  return useCallback(
    (error: unknown, fallback: string) => {
      if (error instanceof AuthenticationError) {
        void signOut()
        return error.message
      }
      return error instanceof Error && error.message.trim() ? error.message : fallback
    },
    [signOut],
  )
}
