import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Bookmark, BookmarkCheck } from 'lucide-react'
import { Button, ButtonLink } from '../../components/Button'
import { useAuth } from '../auth/AuthContext'
import { fetchSavedRecipes, saveRecipe, unsaveRecipe } from '../../services/kitchenApi'
import { useKitchenError } from './useKitchenError'

type SaveRecipeButtonProps = {
  recipeId: string
  recipeName: string
}

export function SaveRecipeButton({ recipeId, recipeName }: SaveRecipeButtonProps) {
  const { user, isLoading } = useAuth()
  const handleError = useKitchenError()
  const [checking, setChecking] = useState(true)
  const [saved, setSaved] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const location = useLocation()

  useEffect(() => {
    if (!user) {
      setChecking(false)
      return
    }
    let mounted = true
    setChecking(true)
    fetchSavedRecipes()
      .then((items) => { if (mounted) setSaved(items.some((item) => item.recipe.id === recipeId)) })
      .catch((e: unknown) => { if (mounted) setError(handleError(e, 'Failed to check saved recipes.')) })
      .finally(() => { if (mounted) setChecking(false) })
    return () => { mounted = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, recipeId])

  if (isLoading) return null

  if (!user) {
    return (
      <div className="mt-6">
        <ButtonLink to="/login" variant="ghost" state={{ from: location.pathname }}>
          <Bookmark size={16} aria-hidden="true" /> Sign in to save this recipe
        </ButtonLink>
      </div>
    )
  }

  async function toggle() {
    setBusy(true)
    setError(null)
    try {
      if (saved) {
        await unsaveRecipe(recipeId)
        setSaved(false)
      } else {
        await saveRecipe(recipeId)
        setSaved(true)
      }
    } catch (e: unknown) {
      setError(handleError(e, saved ? 'Failed to remove this saved recipe.' : 'Failed to save this recipe.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-6">
      <div className="flex flex-wrap items-center gap-3">
        <Button type="button" variant={saved ? 'secondary' : 'ghost'} disabled={checking || busy} onClick={() => void toggle()}>
          {saved ? <BookmarkCheck size={16} aria-hidden="true" /> : <Bookmark size={16} aria-hidden="true" />}
          {checking ? 'Checking…' : saved ? 'Saved' : busy ? 'Saving…' : 'Save recipe'}
        </Button>
        <span className="text-sm text-forest/65">{saved ? `${recipeName} is in your saved recipes.` : 'Keep this recipe in your kitchen.'}</span>
      </div>
      {error ? <p role="alert" className="mt-2 text-sm text-red-700">{error}</p> : null}
    </div>
  )
}
