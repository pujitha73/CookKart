import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Clock, Search, Sparkles } from 'lucide-react'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import {
  MEAL_TYPE_FILTERS,
  fetchRecipeCollections,
  fetchRecipes,
  formatRecipeTime,
  mealTypeLabel,
  type Recipe,
  type RecipeCollection,
} from '../services/recipeApi'

export function RecipesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [collections, setCollections] = useState<RecipeCollection[]>([])
  const [recipes, setRecipes] = useState<Recipe[]>([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const page = Math.max(1, Number(searchParams.get('page') || '1'))
  const collection = searchParams.get('collection') || ''
  const mealType = searchParams.get('meal') || ''
  const search = searchParams.get('q') || ''
  const [searchInput, setSearchInput] = useState(search)

  useEffect(() => {
    setSearchInput(search)
  }, [search])

  useEffect(() => {
    let mounted = true
    fetchRecipeCollections()
      .then((data) => mounted && setCollections(data))
      .catch(() => mounted && setCollections([]))
    return () => { mounted = false }
  }, [])

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    fetchRecipes({
      page,
      page_size: 12,
      collection: collection || undefined,
      meal_type: mealType || undefined,
      search: search || undefined,
    })
      .then((data) => {
        if (!mounted) return
        setRecipes(data.items)
        setTotal(data.total)
        setPages(data.pages)
      })
      .catch((e: unknown) => {
        if (!mounted) return
        setError(e instanceof Error ? e.message : 'Failed to load recipes')
        setRecipes([])
        setTotal(0)
        setPages(0)
      })
      .finally(() => mounted && setLoading(false))
    return () => { mounted = false }
  }, [page, collection, mealType, search])

  const activeCollectionName = useMemo(
    () => collections.find((item) => item.slug === collection)?.name,
    [collections, collection],
  )

  function updateParams(next: { page?: number; collection?: string; meal?: string; q?: string }) {
    const params = new URLSearchParams(searchParams)
    if (next.collection !== undefined) {
      if (next.collection) params.set('collection', next.collection); else params.delete('collection')
      params.set('page', '1')
    }
    if (next.meal !== undefined) {
      if (next.meal) params.set('meal', next.meal); else params.delete('meal')
      params.set('page', '1')
    }
    if (next.q !== undefined) {
      if (next.q) params.set('q', next.q); else params.delete('q')
      params.set('page', '1')
    }
    if (next.page !== undefined) params.set('page', String(next.page))
    setSearchParams(params)
  }

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mb-8 md:mb-10">
          <p className="eyebrow">Explore Recipes</p>
          <h1 className="mt-3 text-4xl md:text-5xl">Find something delicious to cook</h1>
          <p className="mt-4 max-w-2xl text-lg leading-relaxed text-forest/80">
            Browse 25 recipes across five collections. Filter by cuisine or meal type, then open a recipe for ingredients,
            step-by-step instructions and a video guide.
          </p>
        </div>

        <div className="mb-8">
          <h2 className="font-display text-2xl text-forest-dark">Collections</h2>
          <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            {collections.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => updateParams({ collection: collection === item.slug ? '' : item.slug })}
                aria-pressed={collection === item.slug}
                className={`rounded-2xl p-4 text-left transition-all duration-300 ${
                  collection === item.slug
                    ? 'bg-forest text-cream shadow-[var(--shadow-soft)]'
                    : 'bg-white/70 text-forest ring-1 ring-forest/10 hover:-translate-y-1 hover:shadow-[var(--shadow-lift)]'
                }`}
              >
                <Sparkles size={18} aria-hidden="true" />
                <h3 className="mt-3 font-display text-lg">{item.name}</h3>
                <p className={`mt-1 text-xs ${collection === item.slug ? 'text-cream/75' : 'text-forest/65'}`}>
                  {item.recipe_count} recipes · {item.cuisine_label || item.name}
                </p>
              </button>
            ))}
            {!collections.length && !loading ? (
              <p className="text-sm text-forest/60">No collections available yet.</p>
            ) : null}
          </div>
        </div>

        <Card className="mb-6 p-4 md:p-5">
          <div className="flex flex-wrap gap-2">
            {MEAL_TYPE_FILTERS.map((item) => (
              <button
                key={item.value || 'all'}
                type="button"
                onClick={() => updateParams({ meal: item.value })}
                aria-pressed={mealType === item.value}
                className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                  mealType === item.value
                    ? 'bg-forest text-cream'
                    : 'bg-sage-muted/50 text-forest hover:bg-sage-muted'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
          <form
            className="mt-4 flex flex-col gap-3 sm:flex-row"
            onSubmit={(e) => { e.preventDefault(); updateParams({ q: searchInput.trim() }) }}
          >
            <label className="relative block flex-1">
              <span className="sr-only">Search recipes by name</span>
              <Search size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-forest/45" aria-hidden="true" />
              <input
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                type="search"
                placeholder="Search recipes by name"
                className="w-full rounded-full border border-forest/15 bg-white py-3 pl-10 pr-4 text-forest placeholder:text-forest/40 focus:border-lime"
              />
            </label>
            <Button type="submit" variant="primary">Search</Button>
            {(search || collection || mealType) ? (
              <Button type="button" variant="ghost" onClick={() => { setSearchInput(''); setSearchParams(new URLSearchParams()) }}>
                Clear
              </Button>
            ) : null}
          </form>
          <div className="mt-3 text-sm text-forest/70">
            {activeCollectionName ? <span>Collection: <strong className="text-forest-dark">{activeCollectionName}</strong> · </span> : null}
            {mealType ? <span>Meal: <strong className="text-forest-dark">{mealTypeLabel(mealType)}</strong> · </span> : null}
            {search ? <span>Search: <strong className="text-forest-dark">“{search}”</strong> · </span> : null}
            <span>{loading ? 'Loading…' : `${total} recipe${total === 1 ? '' : 's'}`}</span>
          </div>
        </Card>

        {loading ? (
          <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="card-surface animate-pulse p-4">
                <div className="h-44 rounded-2xl bg-sage-muted/50" />
                <div className="mt-4 h-4 w-2/3 rounded bg-sage-muted/50" />
                <div className="mt-2 h-4 w-1/3 rounded bg-sage-muted/50" />
              </div>
            ))}
          </div>
        ) : error ? (
          <Card className="p-8 text-center">
            <p className="eyebrow">Unable to load recipes</p>
            <p className="mt-3 text-lg text-forest-dark">{error}</p>
            <p className="mt-2 text-sm text-forest/70">Please ensure the backend API is running and try again.</p>
            <div className="mt-5"><Button variant="primary" onClick={() => window.location.reload()}>Retry</Button></div>
          </Card>
        ) : recipes.length === 0 ? (
          <Card className="p-10 text-center">
            <p className="eyebrow">No recipes found</p>
            <h2 className="mt-3 text-3xl">Nothing matches those filters</h2>
            <p className="mt-3 text-forest/75">Try a different collection, meal type or search term.</p>
          </Card>
        ) : (
          <>
            <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
              {recipes.map((recipe) => (
                <Link key={recipe.id} to={`/recipes/${recipe.slug}`} className="group block">
                  <Card className="h-full overflow-hidden p-3 transition-all duration-300 group-hover:-translate-y-1 group-hover:shadow-[var(--shadow-lift)]">
                    <ExternalImage
                      src={recipe.image_url || ''}
                      alt={recipe.name}
                      className="h-44 w-full rounded-[1rem] object-cover"
                      sizes="(min-width: 1280px) 20vw, (min-width: 640px) 40vw, 100vw"
                    />
                    <div className="p-2 pt-4">
                      <p className="text-xs font-semibold uppercase tracking-[0.14em] text-forest/60">
                        {recipe.collection?.name || 'Recipe'} · {mealTypeLabel(recipe.meal_type)}
                      </p>
                      <h3 className="mt-1 text-xl text-forest-dark">{recipe.name}</h3>
                      {recipe.description ? (
                        <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-forest/75">{recipe.description}</p>
                      ) : null}
                      <p className="mt-4 flex items-center gap-2 text-sm font-semibold text-forest/75">
                        <Clock size={16} aria-hidden="true" />
                        Prep {formatRecipeTime(recipe.prep_time_minutes)} · Cook {formatRecipeTime(recipe.cook_time_minutes)}
                      </p>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>

            {pages > 1 ? (
              <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                <Button variant="ghost" disabled={page <= 1} onClick={() => updateParams({ page: page - 1 })}>Previous</Button>
                <span className="px-3 text-sm font-semibold text-forest/75">Page {page} of {pages}</span>
                <Button variant="ghost" disabled={page >= pages} onClick={() => updateParams({ page: page + 1 })}>Next</Button>
              </div>
            ) : null}
          </>
        )}
      </div>
    </section>
  )
}
