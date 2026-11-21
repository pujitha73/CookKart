import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AlertCircle, ArrowLeft, Banknote, CheckCircle2, RefreshCw, ShoppingBasket } from 'lucide-react'
import { Button, ButtonLink } from '../components/Button'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import { useCart } from '../features/cart/CartContext'
import { formatPrice } from '../services/catalogApi'
import { placeOrder, type DeliveryAddress } from '../services/orderApi'
import { formatQuantity } from '../utils/formatQuantity'

type FormState = {
  recipient_name: string
  phone: string
  address_line1: string
  address_line2: string
  city: string
  postal_code: string
}

type FieldErrors = Partial<Record<keyof FormState, string>>

const EMPTY_FORM: FormState = {
  recipient_name: '',
  phone: '',
  address_line1: '',
  address_line2: '',
  city: '',
  postal_code: '',
}

const FIELD_CLASS =
  'w-full rounded-2xl border border-forest/15 bg-white px-4 py-3 text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0'

function validate(form: FormState): FieldErrors {
  const errors: FieldErrors = {}
  const recipient = form.recipient_name.trim()
  const phone = form.phone.trim()
  const line1 = form.address_line1.trim()
  const line2 = form.address_line2.trim()
  const city = form.city.trim()
  const postal = form.postal_code.trim()

  if (recipient.length < 2 || recipient.length > 120) errors.recipient_name = 'Enter the recipient’s name (2–120 characters).'
  if (!/^[0-9+()\-\s]{10,20}$/.test(phone)) errors.phone = 'Enter a valid phone number (10–20 digits).'
  if (line1.length < 5 || line1.length > 200) errors.address_line1 = 'Enter the street address (at least 5 characters).'
  if (line2.length > 200) errors.address_line2 = 'Keep this line under 200 characters.'
  if (city.length < 2 || city.length > 100) errors.city = 'Enter the city or town.'
  if (!/^[A-Za-z0-9][A-Za-z0-9 -]{2,19}$/.test(postal)) errors.postal_code = 'Enter a valid postal code.'
  return errors
}

function fieldError(errors: FieldErrors, field: keyof FormState) {
  return errors[field] ? (
    <p role="alert" className="mt-1.5 text-xs font-semibold text-red-700">
      {errors[field]}
    </p>
  ) : null
}

export function CheckoutPage() {
  const { cart, itemCount, loading, error: cartError, refreshCart } = useCart()
  const navigate = useNavigate()
  const [form, setForm] = useState<FormState>(EMPTY_FORM)
  const [errors, setErrors] = useState<FieldErrors>({})
  const [submitError, setSubmitError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  function setField(field: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [field]: value }))
    setErrors((current) => ({ ...current, [field]: undefined }))
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (submitting) return
    setSubmitError(null)

    const nextErrors = validate(form)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    if (!cart || cart.items.length === 0) {
      setSubmitError('Your cart is empty. Add products before placing an order.')
      return
    }

    const address: DeliveryAddress = {
      recipient_name: form.recipient_name.trim(),
      phone: form.phone.trim(),
      address_line1: form.address_line1.trim(),
      address_line2: form.address_line2.trim() || null,
      city: form.city.trim(),
      postal_code: form.postal_code.trim(),
    }

    setSubmitting(true)
    try {
      const order = await placeOrder(address)
      await refreshCart()
      navigate(`/orders/${order.id}`, { replace: true, state: { confirmed: true } })
    } catch (e: unknown) {
      setSubmitError(e instanceof Error ? e.message : 'Failed to place your order. Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <section className="section-space">
        <div className="container-page">
          <div className="mx-auto max-w-5xl animate-pulse">
            <div className="h-5 w-32 rounded bg-sage-muted/50" />
            <div className="mt-6 h-10 w-2/3 rounded bg-sage-muted/50" />
            <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_340px]">
              <div className="h-96 rounded-2xl bg-sage-muted/50" />
              <div className="h-64 rounded-2xl bg-sage-muted/50" />
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (cartError) {
    return (
      <section className="section-space">
        <div className="container-page">
          <Card className="mx-auto max-w-2xl p-8 text-center">
            <p className="eyebrow">Unable to load cart</p>
            <h1 className="mt-3 text-3xl">We couldn’t prepare checkout</h1>
            <p role="alert" className="mt-3 text-forest/75">{cartError}</p>
            <div className="mt-5">
              <Button type="button" onClick={() => void refreshCart()}>
                <RefreshCw size={16} aria-hidden="true" /> Retry
              </Button>
            </div>
          </Card>
        </div>
      </section>
    )
  }

  if (!cart || cart.items.length === 0) {
    return (
      <section className="section-space">
        <div className="container-page">
          <Card className="mx-auto max-w-2xl p-10 text-center">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-sage-muted/70 text-forest">
              <ShoppingBasket size={28} aria-hidden="true" />
            </div>
            <p className="eyebrow mt-5">Empty cart</p>
            <h1 className="mt-3 text-3xl">Nothing to check out yet</h1>
            <p className="mx-auto mt-3 max-w-md text-forest/75">
              Add products to your cart before placing a Cash on Delivery order.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <ButtonLink to="/shop">Browse the Shop</ButtonLink>
              <ButtonLink to="/cart" variant="secondary">View cart</ButtonLink>
            </div>
          </Card>
        </div>
      </section>
    )
  }

  const hasUnavailable = cart.unavailable_item_count > 0

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-5xl">
          <Link to="/cart" className="inline-flex items-center gap-2 text-sm font-semibold text-forest hover:text-forest-dark">
            <ArrowLeft size={16} aria-hidden="true" /> Back to cart
          </Link>

          <div className="mt-6 mb-8">
            <p className="eyebrow">Checkout</p>
            <h1 className="mt-3 text-4xl md:text-5xl">Cash on Delivery</h1>
            <p className="mt-4 max-w-2xl text-lg leading-relaxed text-forest/80">
              Confirm your delivery details and review your cart. The final total is calculated from
              current catalogue prices when your order is placed.
            </p>
          </div>

          {submitError ? (
            <div role="alert" className="mb-6 rounded-2xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700 ring-1 ring-red-200">
              {submitError}
            </div>
          ) : null}

          {hasUnavailable ? (
            <div className="mb-6 flex items-start gap-2 rounded-2xl bg-amber-50 px-4 py-3 text-sm text-amber-900 ring-1 ring-amber-200">
              <AlertCircle size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
              Some products in your cart are no longer available. Remove them from your cart before placing an order.
            </div>
          ) : null}

          <form onSubmit={(event) => void handleSubmit(event)} noValidate>
            <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
              <div className="space-y-6">
                <Card className="p-5 md:p-6">
                  <h2 className="font-display text-2xl text-forest-dark">Delivery details</h2>
                  <div className="mt-5 grid gap-4 sm:grid-cols-2">
                    <div className="sm:col-span-2">
                      <label htmlFor="recipient" className="mb-1.5 block text-sm font-semibold text-forest-dark">Recipient name</label>
                      <input id="recipient" value={form.recipient_name} onChange={(e) => setField('recipient_name', e.target.value)} className={FIELD_CLASS} placeholder="Full name" autoComplete="name" />
                      {fieldError(errors, 'recipient_name')}
                    </div>
                    <div>
                      <label htmlFor="phone" className="mb-1.5 block text-sm font-semibold text-forest-dark">Phone number</label>
                      <input id="phone" value={form.phone} onChange={(e) => setField('phone', e.target.value)} className={FIELD_CLASS} placeholder="9876543210" autoComplete="tel" inputMode="tel" />
                      {fieldError(errors, 'phone')}
                    </div>
                    <div>
                      <label htmlFor="postal" className="mb-1.5 block text-sm font-semibold text-forest-dark">Postal code</label>
                      <input id="postal" value={form.postal_code} onChange={(e) => setField('postal_code', e.target.value)} className={FIELD_CLASS} placeholder="560001" autoComplete="postal-code" />
                      {fieldError(errors, 'postal_code')}
                    </div>
                    <div className="sm:col-span-2">
                      <label htmlFor="address1" className="mb-1.5 block text-sm font-semibold text-forest-dark">Address line 1</label>
                      <input id="address1" value={form.address_line1} onChange={(e) => setField('address_line1', e.target.value)} className={FIELD_CLASS} placeholder="House / flat number, street" autoComplete="address-line1" />
                      {fieldError(errors, 'address_line1')}
                    </div>
                    <div className="sm:col-span-2">
                      <label htmlFor="address2" className="mb-1.5 block text-sm font-semibold text-forest-dark">
                        Address line 2 <span className="font-normal text-forest/60">(optional)</span>
                      </label>
                      <input id="address2" value={form.address_line2} onChange={(e) => setField('address_line2', e.target.value)} className={FIELD_CLASS} placeholder="Landmark, area" autoComplete="address-line2" />
                      {fieldError(errors, 'address_line2')}
                    </div>
                    <div className="sm:col-span-2">
                      <label htmlFor="city" className="mb-1.5 block text-sm font-semibold text-forest-dark">City / town</label>
                      <input id="city" value={form.city} onChange={(e) => setField('city', e.target.value)} className={FIELD_CLASS} placeholder="City" autoComplete="address-level2" />
                      {fieldError(errors, 'city')}
                    </div>
                  </div>
                </Card>

                <Card className="p-5 md:p-6">
                  <h2 className="font-display text-2xl text-forest-dark">Your items</h2>
                  <ul className="mt-4 divide-y divide-forest/10">
                    {cart.items.map((item) => (
                      <li key={item.id} className="flex gap-4 py-4 first:pt-0 last:pb-0">
                        <ExternalImage
                          src={item.product.image_url || ''}
                          alt={item.product.name}
                          className="h-20 w-20 rounded-2xl object-cover"
                          sizes="80px"
                        />
                        <div className="min-w-0 flex-1">
                          <p className="font-semibold text-forest-dark">{item.product.name}</p>
                          <p className="mt-1 text-sm text-forest/70">
                            {formatQuantity(item.product.size, item.product.unit) || 'Grocery product'}
                          </p>
                          <p className="mt-1 text-sm text-forest/70">
                            {item.quantity} × {formatPrice(item.unit_price)}
                          </p>
                        </div>
                        <p className="whitespace-nowrap font-semibold text-forest-dark">
                          {formatPrice(item.subtotal)}
                        </p>
                      </li>
                    ))}
                  </ul>
                </Card>
              </div>

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
                      <dt className="font-semibold text-forest-dark">Order total</dt>
                      <dd className="font-bold text-forest-dark">{formatPrice(cart.total)}</dd>
                    </div>
                  </dl>
                  <p className="mt-3 text-xs leading-relaxed text-forest/60">
                    This total is an estimate from your current cart. The final amount is recalculated
                    from live catalogue prices when the order is placed.
                  </p>

                  <div className="mt-5 flex items-start gap-3 rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
                    <Banknote size={18} className="mt-0.5 shrink-0 text-forest" aria-hidden="true" />
                    <div>
                      <p className="font-semibold text-forest-dark">Cash on Delivery</p>
                      <p className="mt-1 text-xs text-forest/70">Pay when your order arrives. No online payment is required.</p>
                    </div>
                  </div>

                  <Button
                    type="submit"
                    variant="primary"
                    size="lg"
                    className="mt-5 w-full"
                    disabled={submitting || hasUnavailable}
                  >
                    {submitting ? (
                      <>Placing order…</>
                    ) : (
                      <>
                        <CheckCircle2 size={18} aria-hidden="true" /> Place order
                      </>
                    )}
                  </Button>
                  <ButtonLink to="/cart" variant="ghost" className="mt-3 w-full">
                    Return to cart
                  </ButtonLink>
                </Card>
              </div>
            </div>
          </form>
        </div>
      </div>
    </section>
  )
}
