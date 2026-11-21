import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { AlertCircle, Check, ShoppingCart } from 'lucide-react'
import { Button, ButtonLink } from '../../components/Button'
import { Card } from '../../components/Card'
import { ExternalImage } from '../../components/ExternalImage'
import { formatPrice } from '../../services/catalogApi'
import {
  addSelectedRecipeProducts,
  fetchRecipeCartPlan,
  type MissingProduct,
  type RecipeCartPlan,
} from '../../services/cartApi'
import { formatIngredientAmount } from '../../services/recipeApi'
import { useAuth } from '../auth/AuthContext'
import { useKitchenError } from '../kitchen/useKitchenError'
import { useCart } from './CartContext'

type Props = {
  recipeSlug: string
  recipeName: string
  compact?: boolean
}

type SelectedProduct = MissingProduct & { ingredientName: string }

const STATUS_COPY: Record<RecipeCartPlan['missing_ingredients'][number]['status'], string> = {
  available: 'Shop matches found',
  unmapped: 'No product mapping in the catalogue',
  unavailable: 'Mapped products are currently unavailable',
}

export function RecipeCartPanel({ recipeSlug, recipeName, compact = false }: Props) {
  const { user } = useAuth()
  const userId = user?.id
  const location = useLocation()
  const handleError = useKitchenError()
  const { replaceCart } = useCart()
  const [open, setOpen] = useState(false)
  const [plan, setPlan] = useState<RecipeCartPlan | null>(null)
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const [reviewing, setReviewing] = useState(false)
  const [loading, setLoading] = useState(false)
  const [adding, setAdding] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    setOpen(false)
    setPlan(null)
    setSelected(new Set())
    setReviewing(false)
    setError(null)
    setSuccess(null)
  }, [recipeSlug, userId])

  const selectedProducts = useMemo<SelectedProduct[]>(() => {
    if (!plan) return []
    const byId = new Map<string, SelectedProduct>()
    for (const ingredient of plan.missing_ingredients) {
      for (const product of ingredient.products) {
        if (selected.has(product.id) && !byId.has(product.id)) {
          byId.set(product.id, { ...product, ingredientName: ingredient.name })
        }
      }
    }
    return [...byId.values()].sort((a, b) => a.name.localeCompare(b.name))
  }, [plan, selected])

  async function openPanel() {
    setOpen(true)
    setError(null)
    setSuccess(null)
    if (plan) return

    setLoading(true)
    try {
      setPlan(await fetchRecipeCartPlan(recipeSlug))
    } catch (e: unknown) {
      setError(handleError(e, 'Failed to find matching grocery products.'))
    } finally {
      setLoading(false)
    }
  }

  function toggleProduct(productId: string) {
    setSuccess(null)
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(productId)) next.delete(productId)
      else next.add(productId)
      return next
    })
  }

  async function addSelected() {
    if (!selectedProducts.length) return
    setAdding(true)
    setError(null)
    setSuccess(null)
    try {
      const result = await addSelectedRecipeProducts(
        recipeSlug,
        selectedProducts.map((product) => product.id),
      )
      replaceCart(result.cart)
      setSuccess(
        `Added ${result.products_added} grocery product${result.products_added === 1 ? '' : 's'} to your cart.`,
      )
      setSelected(new Set())
      setReviewing(false)
    } catch (e: unknown) {
      setError(handleError(e, 'Failed to add the selected products to your cart.'))
    } finally {
      setAdding(false)
    }
  }

  const loginPath = `${location.pathname}${location.search}`
  const actionLabel = compact ? 'Add missing to cart' : 'Add missing ingredients to cart'

  return (
    <div className={compact ? 'mt-4' : 'mt-6'}>
      {!user ? (
        <ButtonLink
          to="/login"
          state={{ from: loginPath }}
          variant="secondary"
          className={compact ? 'w-full text-xs' : ''}
        >
          <ShoppingCart size={compact ? 14 : 16} aria-hidden="true" /> {actionLabel}
        </ButtonLink>
      ) : (
        <Button
          type="button"
          variant={open ? 'ghost' : 'secondary'}
          onClick={() => (open ? setOpen(false) : void openPanel())}
          className={compact ? 'w-full text-xs' : ''}
        >
          <ShoppingCart size={compact ? 14 : 16} aria-hidden="true" />
          {open ? 'Hide product matching' : actionLabel}
        </Button>
      )}

      {error ? (
        <p role="alert" className="mt-2 text-sm font-semibold text-red-700">
          {error}
        </p>
      ) : null}

      {success ? (
        <div
          role="status"
          className="mt-3 flex flex-wrap items-center gap-2 rounded-2xl bg-sage-muted/60 px-4 py-3 text-sm font-semibold text-forest-dark ring-1 ring-forest/10"
        >
          <Check size={16} aria-hidden="true" />
          {success}
          <Link to="/cart" className="font-bold text-forest underline underline-offset-2">
            View cart
          </Link>
        </div>
      ) : null}

      {open && user ? (
        <Card className={`${compact ? 'mt-3 p-3' : 'mt-4 p-5 md:p-6'} bg-white/70`}>
          {loading ? (
            <div className="animate-pulse space-y-3" aria-label="Loading matching products">
              <div className="h-4 w-1/2 rounded bg-sage-muted/50" />
              <div className="h-16 rounded-2xl bg-sage-muted/50" />
              <div className="h-16 rounded-2xl bg-sage-muted/50" />
            </div>
          ) : !plan ? (
            <p className="text-sm text-forest/70">No product information is available yet.</p>
          ) : (
            <>
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="eyebrow">Smart Recipe-to-Cart</p>
                  <h3 className={`${compact ? 'mt-1 text-lg' : 'mt-2 text-2xl'} font-display text-forest-dark`}>
                    Missing ingredients for {recipeName}
                  </h3>
                </div>
                <span className="rounded-full bg-sage-muted/60 px-3 py-1 text-xs font-semibold text-forest">
                  {plan.missing_count} missing · {plan.matched_missing_count} with shop matches
                </span>
              </div>

              <p className="mt-3 rounded-2xl bg-cream-deep/70 p-3 text-xs leading-relaxed text-forest/75">
                {plan.quantity_note} Recipe amounts below are displayed for reference only.
              </p>

              {reviewing ? (
                <div className="mt-4 rounded-2xl bg-white p-4 ring-1 ring-forest/10">
                  <p className="font-display text-xl text-forest-dark">Review your selection</p>
                  <p className="mt-1 text-sm text-forest/70">
                    Each product below will be added to your cart at quantity 1.
                  </p>
                  <ul className="mt-3 divide-y divide-forest/10">
                    {selectedProducts.map((product) => (
                      <li key={product.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                        <span className="text-forest-dark">
                          {product.name}
                          <span className="block text-xs text-forest/60">For {product.ingredientName}</span>
                        </span>
                        <span className="shrink-0 font-semibold text-forest-dark">
                          1 × {formatPrice(product.price)}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <Button type="button" variant="ghost" onClick={() => setReviewing(false)}>
                      Back to options
                    </Button>
                    <Button type="button" onClick={() => void addSelected()} disabled={adding}>
                      <ShoppingCart size={16} aria-hidden="true" />
                      {adding ? 'Adding…' : `Add ${selectedProducts.length} to cart`}
                    </Button>
                  </div>
                </div>
              ) : plan.missing_ingredients.length === 0 ? (
                <p className="mt-4 rounded-2xl bg-sage-muted/50 p-4 text-sm text-forest-dark">
                  Nothing is missing from your pantry for this recipe.
                </p>
              ) : (
                <ul className="mt-4 space-y-4">
                  {plan.missing_ingredients.map((ingredient) => {
                    const amount = formatIngredientAmount(ingredient.quantity, ingredient.unit)
                    return (
                      <li key={ingredient.id} className="rounded-2xl bg-white p-3 ring-1 ring-forest/10">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <p className="font-semibold text-forest-dark">
                            {ingredient.name}
                            {amount ? (
                              <span className="ml-2 text-sm font-normal text-forest/65">Recipe needs {amount}</span>
                            ) : null}
                          </p>
                          <span
                            className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${
                              ingredient.status === 'available'
                                ? 'bg-sage-muted/70 text-forest'
                                : 'bg-cream-deep text-forest/70'
                            }`}
                          >
                            {STATUS_COPY[ingredient.status]}
                          </span>
                        </div>

                        {ingredient.products.length ? (
                          <div className="mt-3 grid gap-2">
                            {ingredient.products.map((product) => {
                              const checkboxId = `recipe-cart-${ingredient.id}-${product.id}`
                              return (
                                <label
                                  key={product.id}
                                  htmlFor={checkboxId}
                                  className="flex min-w-0 cursor-pointer items-center gap-3 rounded-xl bg-cream/70 p-2 ring-1 ring-forest/10 transition hover:bg-cream"
                                >
                                  <input
                                    id={checkboxId}
                                    type="checkbox"
                                    checked={selected.has(product.id)}
                                    onChange={() => toggleProduct(product.id)}
                                    className="h-4 w-4 shrink-0 accent-[#1f3d2b]"
                                  />
                                  <ExternalImage
                                    src={product.image_url || ''}
                                    alt={product.name}
                                    className="h-12 w-12 shrink-0 rounded-lg object-cover"
                                    sizes="48px"
                                  />
                                  <span className="min-w-0 flex-1">
                                    <span className="block truncate text-sm font-semibold text-forest-dark">
                                      {product.name}
                                    </span>
                                    <span className="block text-xs text-forest/60">
                                      {product.size || product.unit || 'Grocery pack'}
                                      {product.substitution_note ? ` · ${product.substitution_note}` : ''}
                                    </span>
                                  </span>
                                  <span className="shrink-0 text-sm font-semibold text-forest-dark">
                                    {formatPrice(product.price)}
                                  </span>
                                </label>
                              )
                            })}
                          </div>
                        ) : (
                          <p className="mt-2 flex items-center gap-1.5 text-xs text-forest/65">
                            <AlertCircle size={14} aria-hidden="true" />
                            {ingredient.status === 'unmapped'
                              ? 'This ingredient has no product mapping in the catalogue.'
                              : 'Mapped products for this ingredient are unavailable right now.'}
                          </p>
                        )}
                      </li>
                    )
                  })}
                </ul>
              )}

              {!reviewing && selectedProducts.length ? (
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-forest/10 pt-4">
                  <p className="text-sm font-semibold text-forest-dark">
                    {selectedProducts.length} product{selectedProducts.length === 1 ? '' : 's'} selected
                  </p>
                  <Button type="button" onClick={() => setReviewing(true)}>
                    Review selection
                  </Button>
                </div>
              ) : null}
            </>
          )}
        </Card>
      ) : null}
    </div>
  )
}
