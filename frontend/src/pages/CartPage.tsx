import { useState } from 'react'
import { AlertCircle, ArrowRight, RefreshCw, ShoppingBasket, Trash2 } from 'lucide-react'
import { Button, ButtonLink } from '../components/Button'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import { QuantityStepper } from '../components/QuantityStepper'
import { useCart } from '../features/cart/CartContext'
import { formatPrice } from '../services/catalogApi'
import { formatQuantity } from '../utils/formatQuantity'

export function CartPage() {
  const { cart, itemCount, loading, error, refreshCart, changeQuantity, removeProduct } = useCart()
  const [busyItem, setBusyItem] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)

  async function runAction(itemId: string, action: () => Promise<void>) {
    setBusyItem(itemId)
    setActionError(null)
    try {
      await action()
    } catch (e: unknown) {
      setActionError(e instanceof Error ? e.message : 'This cart change could not be completed.')
    } finally {
      setBusyItem(null)
    }
  }

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mb-8 md:mb-10">
          <p className="eyebrow">Your basket</p>
          <h1 className="mt-3 text-4xl md:text-5xl">Shopping cart</h1>
          <p className="mt-4 max-w-2xl text-lg leading-relaxed text-forest/80">
            Review the grocery products saved to your account. Quantities and prices are read from the
            live catalogue.
          </p>
        </div>

        {loading ? (
          <div className="grid gap-6 lg:grid-cols-[1fr_320px]" aria-label="Loading cart">
            <div className="card-surface animate-pulse p-5">
              {Array.from({ length: 3 }).map((_, index) => (
                <div key={index} className="mb-5 flex gap-4">
                  <div className="h-24 w-24 rounded-2xl bg-sage-muted/50" />
                  <div className="flex-1 space-y-3">
                    <div className="h-4 w-1/2 rounded bg-sage-muted/50" />
                    <div className="h-4 w-1/3 rounded bg-sage-muted/50" />
                    <div className="h-8 w-28 rounded-full bg-sage-muted/50" />
                  </div>
                </div>
              ))}
            </div>
            <div className="card-surface h-52 animate-pulse p-5" />
          </div>
        ) : error ? (
          <Card className="mx-auto max-w-2xl p-8 text-center">
            <p className="eyebrow">Unable to load cart</p>
            <h2 className="mt-3 text-3xl">We couldn’t open your basket</h2>
            <p role="alert" className="mt-3 text-forest/75">{error}</p>
            <div className="mt-5">
              <Button type="button" onClick={() => void refreshCart()}>
                <RefreshCw size={16} aria-hidden="true" /> Retry
              </Button>
            </div>
          </Card>
        ) : !cart || cart.items.length === 0 ? (
          <Card className="mx-auto max-w-2xl p-10 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-sage-muted/70 text-forest">
              <ShoppingBasket size={28} aria-hidden="true" />
            </div>
            <p className="eyebrow mt-5">Empty cart</p>
            <h2 className="mt-3 text-3xl">Your basket is ready for groceries</h2>
            <p className="mx-auto mt-3 max-w-md text-forest/75">
              Browse the Shop to add products, or open a recipe and add the ingredients you are missing.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <ButtonLink to="/shop">Browse the Shop</ButtonLink>
              <ButtonLink to="/recipes" variant="secondary">Explore Recipes</ButtonLink>
            </div>
          </Card>
        ) : (
          <>
            {actionError ? (
              <div role="alert" className="mb-5 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700 ring-1 ring-red/20">
                {actionError}
              </div>
            ) : null}
            {cart.unavailable_item_count ? (
              <div className="mb-5 flex items-start gap-2 rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-900 ring-1 ring-amber-200">
                <AlertCircle size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
                Some products in your cart are no longer available. Quantity changes are disabled for
                those items.
              </div>
            ) : null}

            <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
              <Card className="p-4 md:p-6">
                <ul className="divide-y divide-forest/10">
                  {cart.items.map((item) => {
                    const unavailable = !item.product.is_available
                    const itemBusy = busyItem === item.id
                    return (
                      <li key={item.id} className="grid gap-4 py-5 first:pt-0 last:pb-0 sm:grid-cols-[96px_1fr_auto]">
                        <ExternalImage
                          src={item.product.image_url || ''}
                          alt={item.product.name}
                          className="h-24 w-24 rounded-2xl object-cover"
                          sizes="96px"
                        />
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <p className="text-lg font-semibold text-forest-dark">{item.product.name}</p>
                            {unavailable ? (
                              <span className="rounded-full bg-red-50 px-2.5 py-1 text-[11px] font-semibold text-red-700">
                                Unavailable
                              </span>
                            ) : null}
                          </div>
                          <p className="mt-1 text-sm text-forest/65">
                            {formatQuantity(item.product.size, item.product.unit) || 'Grocery product'}
                          </p>
                          <p className="mt-2 text-sm font-semibold text-forest-dark">
                            {formatPrice(item.unit_price)} each
                          </p>

                          <div className="mt-3 flex flex-wrap items-center gap-2">
                            <QuantityStepper
                              value={item.quantity}
                              onChange={(next) =>
                                void runAction(item.id, () => changeQuantity(item.id, next))
                              }
                              label={item.product.name}
                              disabled={itemBusy || unavailable}
                            />
                            <button
                              type="button"
                              className="inline-flex items-center gap-1.5 rounded-full px-3 py-2 text-xs font-semibold text-forest/70 transition hover:bg-red-50 hover:text-red-700 disabled:cursor-not-allowed disabled:opacity-40"
                              disabled={itemBusy}
                              onClick={() => void runAction(item.id, () => removeProduct(item.id))}
                            >
                              <Trash2 size={14} aria-hidden="true" /> Remove
                            </button>
                          </div>
                        </div>
                        <div className="sm:text-right">
                          <p className="text-xs font-semibold uppercase tracking-wider text-forest/55">
                            Subtotal
                          </p>
                          <p className="mt-1 text-xl font-semibold text-forest-dark">
                            {formatPrice(item.subtotal)}
                          </p>
                        </div>
                      </li>
                    )
                  })}
                </ul>
              </Card>

              <div className="space-y-4 lg:sticky lg:top-28 lg:self-start">
                <Card className="p-5">
                  <h2 className="font-display text-2xl text-forest-dark">Order summary</h2>
                  <dl className="mt-4 space-y-3 text-sm">
                    <div className="flex justify-between gap-3">
                      <dt className="text-forest/70">Products</dt>
                      <dd className="font-semibold text-forest-dark">{cart.line_count}</dd>
                    </div>
                    <div className="flex justify-between gap-3">
                      <dt className="text-forest/70">Total quantity</dt>
                      <dd className="font-semibold text-forest-dark">{itemCount}</dd>
                    </div>
                    <div className="flex justify-between gap-3 border-t border-forest/10 pt-3 text-base">
                      <dt className="font-semibold text-forest-dark">Cart total</dt>
                      <dd className="font-bold text-forest-dark">{formatPrice(cart.total)}</dd>
                    </div>
                  </dl>
                  {cart.unavailable_item_count ? (
                    <p className="mt-4 text-xs leading-relaxed text-red-700">
                      Remove unavailable products from your cart before checkout.
                    </p>
                  ) : (
                    <div className="mt-5">
                      <ButtonLink to="/checkout" className="w-full">
                        Proceed to checkout <ArrowRight size={16} aria-hidden="true" />
                      </ButtonLink>
                    </div>
                  )}
                  <div className="mt-3">
                    <ButtonLink to="/shop" variant="secondary" className="w-full">
                      Continue shopping <ArrowRight size={16} aria-hidden="true" />
                    </ButtonLink>
                  </div>
                </Card>
              </div>
            </div>
          </>
        )}
      </div>
    </section>
  )
}
