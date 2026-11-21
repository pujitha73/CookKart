import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Clock, Play, Users } from 'lucide-react'
import { ButtonLink } from '../components/Button'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import { RecipeCartPanel } from '../features/cart/RecipeCartPanel'
import { SaveRecipeButton } from '../features/kitchen/SaveRecipeButton'
import {
  fetchRecipeBySlug,
  formatIngredientAmount,
  formatRecipeTime,
  mealTypeLabel,
  type RecipeDetail,
} from '../services/recipeApi'

/** Only allow well-formed HTTPS links to YouTube in the fallback link. */
function safeYoutubeLink(value?: string | null): string | null {
  if (!value) return null
  try {
    const url = new URL(value)
    if (url.protocol !== 'https:') return null
    if (!['www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be'].includes(url.hostname)) {
      return null
    }
    return url.toString()
  } catch {
    return null
  }
}

export function RecipeDetailPage() {
  const { slug } = useParams()
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [playing, setPlaying] = useState(false)

  useEffect(() => {
    if (!slug) return
    let mounted = true
    setLoading(true)
    setError(null)
    setPlaying(false)
    setRecipe(null)
    fetchRecipeBySlug(slug)
      .then((data) => mounted && setRecipe(data))
      .catch((e: unknown) => mounted && setError(e instanceof Error ? e.message : 'Failed to load recipe'))
      .finally(() => mounted && setLoading(false))
    return () => { mounted = false }
  }, [slug])

  if (loading) {
    return (
      <section className="section-space">
        <div className="container-page">
          <div className="mx-auto max-w-5xl animate-pulse">
            <div className="h-5 w-32 rounded bg-sage-muted/50" />
            <div className="mt-6 grid gap-8 lg:grid-cols-2">
              <div className="h-[380px] rounded-[1.25rem] bg-sage-muted/50" />
              <div className="space-y-4 pt-4">
                <div className="h-8 w-3/4 rounded bg-sage-muted/50" />
                <div className="h-5 w-1/3 rounded bg-sage-muted/50" />
                <div className="h-24 w-full rounded bg-sage-muted/50" />
              </div>
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (error || !recipe) {
    return (
      <section className="section-space">
        <div className="container-page">
          <Card className="mx-auto max-w-2xl p-8 text-center">
            <p className="eyebrow">Recipe unavailable</p>
            <h1 className="mt-3 text-3xl md:text-4xl">We couldn’t load this recipe</h1>
            <p className="mt-4 text-forest/75">{error || 'The recipe may not exist.'}</p>
            <div className="mt-6 flex justify-center gap-3">
              <ButtonLink to="/recipes" variant="primary"><ArrowLeft size={16} aria-hidden="true" /> Back to Explore Recipes</ButtonLink>
            </div>
          </Card>
        </div>
      </section>
    )
  }

  const videoId = recipe.youtube_video_id && /^[A-Za-z0-9_-]{11}$/.test(recipe.youtube_video_id)
    ? recipe.youtube_video_id
    : null
  const youtubeLink = safeYoutubeLink(recipe.youtube_url)

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-5xl">
          <Link to="/recipes" className="inline-flex items-center gap-2 text-sm font-semibold text-forest hover:text-forest-dark">
            <ArrowLeft size={16} aria-hidden="true" /> Back to Explore Recipes
          </Link>

          <div className="mt-6 grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
            <Card className="overflow-hidden p-3">
              <ExternalImage
                src={recipe.image_url || ''}
                alt={recipe.name}
                className="h-[340px] w-full rounded-[1rem] object-cover md:h-[460px]"
                priority
                sizes="(min-width: 1024px) 45vw, 100vw"
              />
            </Card>
            <div className="flex flex-col">
              <p className="eyebrow">
                {recipe.collection?.name || 'Recipe'} · {mealTypeLabel(recipe.meal_type)}
              </p>
              <h1 className="mt-3 text-4xl md:text-5xl">{recipe.name}</h1>
              {recipe.description ? (
                <p className="mt-5 text-lg leading-relaxed text-forest/80">{recipe.description}</p>
              ) : null}

              <SaveRecipeButton recipeId={recipe.id} recipeName={recipe.name} />

              <div className="mt-7 grid grid-cols-2 gap-3 sm:grid-cols-4">
                <div className="rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
                  <p className="text-xs uppercase tracking-wider text-forest/60">Prep</p>
                  <p className="mt-1 font-semibold text-forest-dark">{formatRecipeTime(recipe.prep_time_minutes)}</p>
                </div>
                <div className="rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
                  <p className="text-xs uppercase tracking-wider text-forest/60">Cook</p>
                  <p className="mt-1 font-semibold text-forest-dark">{formatRecipeTime(recipe.cook_time_minutes)}</p>
                </div>
                <div className="rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
                  <p className="text-xs uppercase tracking-wider text-forest/60">Serves</p>
                  <p className="mt-1 font-semibold text-forest-dark">{recipe.serving_size || '—'}</p>
                </div>
                <div className="rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
                  <p className="text-xs uppercase tracking-wider text-forest/60">Level</p>
                  <p className="mt-1 font-semibold text-forest-dark">{recipe.difficulty || '—'}</p>
                </div>
              </div>

              <p className="mt-5 flex items-center gap-2 text-sm text-forest/65">
                <Clock size={16} aria-hidden="true" />
                Total time {formatRecipeTime((recipe.prep_time_minutes || 0) + (recipe.cook_time_minutes || 0))}
                <Users size={16} className="ml-3" aria-hidden="true" />
                {recipe.serving_size || '—'} serving{recipe.serving_size === 1 ? '' : 's'}
              </p>
            </div>
          </div>

          <div className="mt-10 grid gap-8 lg:grid-cols-2">
            <Card className="p-5 md:p-6">
              <h2 className="font-display text-2xl text-forest-dark">Ingredients</h2>
              {recipe.ingredients.length ? (
                <ul className="mt-4 divide-y divide-forest/10">
                  {recipe.ingredients.map((item) => (
                    <li key={`${item.name}-${item.display_order}`} className="flex items-center justify-between gap-4 py-3">
                      <span className="text-forest-dark">{item.name}</span>
                      <span className="shrink-0 text-sm font-semibold text-forest/70">
                        {formatIngredientAmount(item.quantity, item.unit)}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="mt-4 text-forest/70">Ingredient details are not available for this recipe.</p>
              )}
            </Card>

            <Card className="p-5 md:p-6">
              <h2 className="font-display text-2xl text-forest-dark">Watch the recipe</h2>
              {videoId ? (
                <div className="mt-4 overflow-hidden rounded-2xl bg-forest/5 ring-1 ring-forest/10">
                  {playing ? (
                    <iframe
                      className="aspect-video w-full"
                      src={`https://www.youtube-nocookie.com/embed/${videoId}?autoplay=1&rel=0`}
                      title={`Video guide for ${recipe.name}`}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                      referrerPolicy="strict-origin-when-cross-origin"
                      allowFullScreen
                    />
                  ) : (
                    <button
                      type="button"
                      onClick={() => setPlaying(true)}
                      aria-label={`Play video guide for ${recipe.name}`}
                      className="group relative block w-full"
                    >
                      <ExternalImage
                        src={`https://i.ytimg.com/vi/${videoId}/hqdefault.jpg`}
                        alt={`Video thumbnail for ${recipe.name}`}
                        className="aspect-video w-full object-cover"
                      />
                      <span className="absolute inset-0 flex items-center justify-center bg-forest/25 transition group-hover:bg-forest/35">
                        <span className="flex h-14 w-14 items-center justify-center rounded-full bg-forest text-cream shadow-lg">
                          <Play size={22} fill="currentColor" aria-hidden="true" />
                        </span>
                      </span>
                    </button>
                  )}
                </div>
              ) : (
                <p className="mt-4 text-sm text-forest/70">A video guide is not available for this recipe.</p>
              )}
              {videoId && youtubeLink ? (
                <p className="mt-3 text-sm text-forest/65">
                  If the player does not load,{' '}
                  <a
                    href={youtubeLink}
                    target="_blank"
                    rel="noreferrer"
                    className="font-semibold text-forest-dark underline underline-offset-2"
                  >
                    watch the video on YouTube
                  </a>.
                </p>
              ) : null}
            </Card>
          </div>

          <Card className="mt-8 p-5 md:p-7">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <h2 className="font-display text-2xl text-forest-dark">Smart Recipe-to-Cart</h2>
                <p className="mt-2 max-w-2xl text-sm leading-relaxed text-forest/75">
                  Match missing ingredients to available grocery products, choose the packs you want, and review them before adding.
                </p>
              </div>
            </div>
            <RecipeCartPanel recipeSlug={recipe.slug} recipeName={recipe.name} />
          </Card>

          <Card className="mt-8 p-5 md:p-7">
            <h2 className="font-display text-2xl text-forest-dark">Method</h2>
            {recipe.instructions.length ? (
              <ol className="mt-5 space-y-4">
                {recipe.instructions.map((step, index) => (
                  <li key={`${index}-${step.slice(0, 20)}`} className="flex gap-4">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-forest text-sm font-semibold text-cream">
                      {index + 1}
                    </span>
                    <p className="pt-1 leading-relaxed text-forest/80">{step}</p>
                  </li>
                ))}
              </ol>
            ) : (
              <p className="mt-4 text-forest/70">Instructions are not available for this recipe.</p>
            )}
          </Card>

          <div className="mt-8 flex justify-center">
            <ButtonLink to="/recipes" variant="secondary">Browse more recipes</ButtonLink>
          </div>
        </div>
      </div>
    </section>
  )
}
