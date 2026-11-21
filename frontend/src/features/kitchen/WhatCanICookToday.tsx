import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Check, ChefHat, Clock, RefreshCw, ShoppingBasket, X } from 'lucide-react'
import { Button, ButtonLink } from '../../components/Button'
import { Card } from '../../components/Card'
import { ExternalImage } from '../../components/ExternalImage'
import { RecipeCartPanel } from '../cart/RecipeCartPanel'
import {
  fetchRecommendations,
  type RecommendationListResponse,
} from '../../services/kitchenApi'
import {
  MEAL_TYPE_FILTERS,
  fetchRecipeCollections,
  formatIngredientAmount,
  formatRecipeTime,
  mealTypeLabel,
  type RecipeCollection,
} from '../../services/recipeApi'
import { useKitchenError } from './useKitchenError'

type WhatCanICookTodayProps = {
  pantryVersion: number
}

function matchLabel(value: number): string {
  return Number.isInteger(value) ? String(value) : value.toFixed(1)
}

export function WhatCanICookToday({ pantryVersion }: WhatCanICookTodayProps) {
  const handleError = useKitchenError()
  const [data, setData] = useState<RecommendationListResponse | null>(null)
  const [collections, setCollections] = useState<RecipeCollection[]>([])
  const [mealType, setMealType] = useState('')
  const [collection, setCollection] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [reloadToken, setReloadToken] = useState(0)

  useEffect(() => {
    let mounted = true
    fetchRecipeCollections()
      .then((items) => { if (mounted) setCollections(items) })
      .catch(() => { if (mounted) setCollections([]) })
    return () => { mounted = false }
  }, [])

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    fetchRecommendations({
      meal_type: mealType || undefined,
      collection: collection || undefined,
    })
      .then((result) => { if (mounted) setData(result) })
      .catch((e: unknown) => {
        if (!mounted) return
        setError(handleError(e, 'Failed to load your recipe recommendations.'))
        setData(null)
      })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
  }, [mealType, collection, pantryVersion, reloadToken, handleError])

  function scrollToPantry() {
    document.getElementById('my-pantry')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const filtersActive = Boolean(mealType || collection)

  return (
    <Card className="p-5 md:p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="eyebrow">Pantry recommendations</p>
          <h2 className="mt-2 font-display text-2xl text-forest-dark">What Can I Cook Today?</h2>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-forest/75">
            Recipes are ranked by how much of each recipe you already have on hand. Matches use real pantry
            and recipe ingredient records, and every card shows what is still missing.
          </p>
        </div>
        {!loading && !error && data ? (
          <span className="rounded-full bg-sage-muted/60 px-3 py-1 text-sm font-semibold text-forest">
            {data.total} match{data.total === 1 ? '' : 'es'} · {data.available_ingredient_count} available
            ingredient{data.available_ingredient_count === 1 ? '' : 's'}
          </span>
        ) : null}
      </div>

      <div className="mt-6 rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
        <p className="text-xs font-semibold uppercase tracking-[0.12em] text-forest/60">Meal type</p>
        <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label="Filter recommendations by meal type">
          {MEAL_TYPE_FILTERS.map((item) => (
            <button
              key={item.value || 'all'}
              type="button"
              onClick={() => setMealType(item.value)}
              aria-pressed={mealType === item.value}
              className={`rounded-full px-3.5 py-2 text-sm font-semibold transition ${
                mealType === item.value
                  ? 'bg-forest text-cream'
                  : 'bg-white/70 text-forest ring-1 ring-forest/10 hover:bg-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>

        <p className="mt-4 text-xs font-semibold uppercase tracking-[0.12em] text-forest/60">Collection</p>
        <div className="mt-2 flex flex-wrap gap-2" role="group" aria-label="Filter recommendations by collection">
          <button
            type="button"
            onClick={() => setCollection('')}
            aria-pressed={collection === ''}
            className={`rounded-full px-3.5 py-2 text-sm font-semibold transition ${
              collection === ''
                ? 'bg-forest text-cream'
                : 'bg-white/70 text-forest ring-1 ring-forest/10 hover:bg-white'
            }`}
          >
            All collections
          </button>
          {collections.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => setCollection(item.slug)}
              aria-pressed={collection === item.slug}
              className={`rounded-full px-3.5 py-2 text-sm font-semibold transition ${
                collection === item.slug
                  ? 'bg-forest text-cream'
                  : 'bg-white/70 text-forest ring-1 ring-forest/10 hover:bg-white'
              }`}
            >
              {item.name}
            </button>
          ))}
        </div>

        {filtersActive ? (
          <div className="mt-3">
            <Button type="button" variant="ghost" onClick={() => { setMealType(''); setCollection('') }}>
              Clear filters
            </Button>
          </div>
        ) : null}
      </div>

      {loading ? (
        <div className="mt-6 grid gap-5 sm:grid-cols-2 xl:grid-cols-3" aria-label="Loading recommendations">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="card-surface animate-pulse p-4">
              <div className="h-40 rounded-2xl bg-sage-muted/50" />
              <div className="mt-4 h-4 w-2/3 rounded bg-sage-muted/50" />
              <div className="mt-2 h-3 w-1/2 rounded bg-sage-muted/50" />
              <div className="mt-4 h-16 rounded-2xl bg-sage-muted/50" />
            </div>
          ))}
        </div>
      ) : error ? (
        <div className="mt-6 rounded-2xl bg-white/70 p-6 text-center ring-1 ring-forest/10">
          <p className="font-semibold text-forest-dark">{error}</p>
          <div className="mt-4">
            <Button type="button" onClick={() => setReloadToken((value) => value + 1)}>
              <RefreshCw size={16} aria-hidden="true" /> Retry
            </Button>
          </div>
        </div>
      ) : !data || data.available_ingredient_count === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-forest/20 p-8 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-sage-muted/60 text-forest">
            <ChefHat size={26} aria-hidden="true" />
          </div>
          <p className="mt-4 font-display text-xl text-forest-dark">Your pantry needs a few ingredients</p>
          <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-forest/75">
            Add ingredients above and mark them as available. We will rank real recipes against what you have.
          </p>
          <div className="mt-5">
            <Button type="button" onClick={scrollToPantry}>
              <ShoppingBasket size={16} aria-hidden="true" /> Add pantry ingredients
            </Button>
          </div>
        </div>
      ) : data.items.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-forest/20 p-8 text-center">
          <p className="font-display text-xl text-forest-dark">No matches for these filters</p>
          <p className="mx-auto mt-2 max-w-md text-sm leading-relaxed text-forest/75">
            None of the recipes in this collection share your available ingredients. Try another meal type or
            collection, or add more pantry items.
          </p>
          <div className="mt-5 flex flex-wrap justify-center gap-2">
            <Button type="button" variant="ghost" onClick={() => { setMealType(''); setCollection('') }}>
              Clear filters
            </Button>
            <ButtonLink to="/recipes" variant="secondary">
              Browse all recipes <ArrowRight size={16} aria-hidden="true" />
            </ButtonLink>
          </div>
        </div>
      ) : (
        <div className="mt-6 grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
          {data.items.map((item) => {
            const recipe = item.recipe
            return (
              <div key={recipe.id} className="group block">
                <Card className="h-full overflow-hidden p-3 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-[var(--shadow-lift)]">
                  <div className="relative">
                    <ExternalImage
                      src={recipe.image_url || ''}
                      alt={recipe.name}
                      className="h-40 w-full rounded-[1rem] object-cover"
                      sizes="(min-width: 1280px) 20vw, (min-width: 640px) 40vw, 100vw"
                    />
                    <span className="absolute left-3 top-3 rounded-full bg-forest px-3 py-1.5 text-sm font-bold text-cream shadow-[var(--shadow-soft)]">
                      {matchLabel(item.match_percentage)}% match
                    </span>
                  </div>

                  <div className="p-2 pt-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.14em] text-forest/60">
                      {recipe.collection?.name || 'Recipe'} · {mealTypeLabel(recipe.meal_type)}
                    </p>
                    <h3 className="mt-1 text-xl text-forest-dark">{recipe.name}</h3>
                    {recipe.description ? (
                      <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-forest/75">{recipe.description}</p>
                    ) : null}

                    <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold text-forest/75">
                      <span>
                        {item.matched_count} of {item.required_count} ingredients available
                      </span>
                      <span>{item.missing_count} missing</span>
                    </div>
                    <div
                      className="mt-2 h-2 overflow-hidden rounded-full bg-sage-muted/60"
                      role="progressbar"
                      aria-valuenow={item.match_percentage}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-label={`${recipe.name} ingredient match`}
                    >
                      <div
                        className="h-full rounded-full bg-lime transition-all duration-300"
                        style={{ width: `${item.match_percentage}%` }}
                      />
                    </div>

                    <div className="mt-4 grid gap-3 sm:grid-cols-2">
                      <div>
                        <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-forest/70">
                          <Check size={14} aria-hidden="true" /> Available
                        </p>
                        <ul className="mt-2 flex flex-wrap gap-1.5">
                          {item.available_ingredients.map((ingredient) => {
                            const amount = formatIngredientAmount(ingredient.quantity, ingredient.unit)
                            return (
                              <li
                                key={ingredient.id}
                                className="rounded-full bg-sage-muted/60 px-2.5 py-1 text-xs text-forest"
                              >
                                {ingredient.name}{amount ? ` · ${amount}` : ''}
                              </li>
                            )
                          })}
                        </ul>
                      </div>
                      <div>
                        <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-forest/70">
                          <X size={14} aria-hidden="true" /> Missing
                        </p>
                        <ul className="mt-2 flex flex-wrap gap-1.5">
                          {item.missing_ingredients.length ? (
                            item.missing_ingredients.map((ingredient) => (
                              <li
                                key={ingredient.id}
                                className="rounded-full bg-cream-deep px-2.5 py-1 text-xs text-forest/80 ring-1 ring-forest/10"
                              >
                                {ingredient.name}
                              </li>
                            ))
                          ) : (
                            <li className="text-xs text-forest/60">Nothing missing</li>
                          )}
                        </ul>
                      </div>
                    </div>

                    <div className="mt-4 flex items-center justify-between gap-2 text-sm font-semibold text-forest/75">
                      <span className="flex items-center gap-2">
                        <Clock size={16} aria-hidden="true" />
                        {formatRecipeTime(recipe.prep_time_minutes)}
                      </span>
                      <Link
                        to={`/recipes/${recipe.slug}`}
                        className="flex items-center gap-1 hover:underline"
                      >
                        View recipe <ArrowRight size={15} aria-hidden="true" />
                      </Link>
                    </div>

                    <RecipeCartPanel
                      recipeSlug={recipe.slug}
                      recipeName={recipe.name}
                      compact
                    />
                  </div>
                </Card>
              </div>
            )
          })}
        </div>
      )}
    </Card>
  )
}
