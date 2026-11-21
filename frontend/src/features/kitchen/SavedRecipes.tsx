import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { BookmarkX, Clock } from 'lucide-react'
import { Button, ButtonLink } from '../../components/Button'
import { Card } from '../../components/Card'
import { ExternalImage } from '../../components/ExternalImage'
import { fetchSavedRecipes, unsaveRecipe, type SavedRecipe } from '../../services/kitchenApi'
import { formatRecipeTime, mealTypeLabel } from '../../services/recipeApi'
import { useKitchenError } from './useKitchenError'

export function SavedRecipes() {
  const handleError = useKitchenError()
  const [items, setItems] = useState<SavedRecipe[]>([])
  const [loading, setLoading] = useState(true)
  const [removingId, setRemovingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  async function load() {
    const data = await fetchSavedRecipes()
    setItems(data)
  }

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    load()
      .catch((e: unknown) => { if (mounted) setError(handleError(e, 'Failed to load saved recipes.')) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function remove(recipeId: string, name: string) {
    setRemovingId(recipeId)
    setError(null)
    setSuccess(null)
    try {
      await unsaveRecipe(recipeId)
      await load()
      setSuccess(`${name} removed from saved recipes.`)
    } catch (e) {
      setError(handleError(e, 'Failed to remove this saved recipe.'))
    } finally {
      setRemovingId(null)
    }
  }

  return (
    <Card className="p-5 md:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">Saved Recipes</p>
          <h2 className="mt-2 font-display text-2xl text-forest-dark">Your recipe collection</h2>
        </div>
        {!loading && !error ? (
          <span className="rounded-full bg-sage-muted/60 px-3 py-1 text-sm font-semibold text-forest">
            {items.length} saved
          </span>
        ) : null}
      </div>

      {loading ? (
        <div className="mt-6 grid animate-pulse gap-4 sm:grid-cols-2">
          <div className="h-40 rounded-2xl bg-sage-muted/50" />
          <div className="h-40 rounded-2xl bg-sage-muted/50" />
        </div>
      ) : error ? (
        <div className="mt-6 rounded-2xl bg-white/70 p-5 text-center ring-1 ring-forest/10">
          <p className="font-semibold text-forest-dark">{error}</p>
          <div className="mt-4 flex justify-center gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => {
                setError(null)
                setLoading(true)
                load()
                  .catch((e: unknown) => setError(handleError(e, 'Failed to load saved recipes.')))
                  .finally(() => setLoading(false))
              }}
            >
              Retry
            </Button>
          </div>
        </div>
      ) : (
        <>
          {success ? <p role="status" className="mt-4 text-sm font-semibold text-forest-dark">{success}</p> : null}
          {items.length ? (
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              {items.map(({ id, recipe }) => (
                <div key={id} className="overflow-hidden rounded-2xl bg-white/75 ring-1 ring-forest/10">
                  <div className="flex gap-3 p-3">
                    <Link to={`/recipes/${recipe.slug}`} className="shrink-0">
                      <ExternalImage
                        src={recipe.image_url || ''}
                        alt={recipe.name}
                        className="h-20 w-20 rounded-xl object-cover"
                        sizes="80px"
                      />
                    </Link>
                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-semibold uppercase tracking-[0.12em] text-forest/60">
                        {recipe.collection?.name || 'Recipe'} · {mealTypeLabel(recipe.meal_type)}
                      </p>
                      <Link to={`/recipes/${recipe.slug}`} className="mt-1 block truncate font-display text-lg text-forest-dark hover:underline">
                        {recipe.name}
                      </Link>
                      <p className="mt-1 flex items-center gap-1 text-xs text-forest/65">
                        <Clock size={13} aria-hidden="true" />
                        {formatRecipeTime(recipe.prep_time_minutes)} prep
                      </p>
                    </div>
                  </div>
                  <div className="border-t border-forest/10 px-3 py-2 text-right">
                    <button
                      type="button"
                      onClick={() => void remove(recipe.id, recipe.name)}
                      disabled={removingId === recipe.id}
                      className="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold text-forest hover:bg-sage-muted/60 disabled:opacity-60"
                    >
                      <BookmarkX size={14} aria-hidden="true" />
                      {removingId === recipe.id ? 'Removing…' : 'Remove'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="mt-6 rounded-2xl border border-dashed border-forest/20 p-8 text-center">
              <p className="font-semibold text-forest-dark">No saved recipes yet</p>
              <p className="mt-2 text-sm text-forest/70">Save recipes from their detail pages to find them here.</p>
              <div className="mt-4">
                <ButtonLink to="/recipes" variant="secondary">Explore recipes</ButtonLink>
              </div>
            </div>
          )}
        </>
      )}
    </Card>
  )
}
