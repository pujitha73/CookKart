import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router-dom'
import { ArrowLeft, Banknote, CheckCircle2, MapPin, RefreshCw } from 'lucide-react'
import { Button, ButtonLink } from '../components/Button'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import { formatPrice } from '../services/catalogApi'
import { fetchOrder, type Order } from '../services/orderApi'

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('en-IN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function OrderDetailPage() {
  const { orderId } = useParams<{ orderId: string }>()
  const location = useLocation()
  const confirmed = (location.state as { confirmed?: boolean } | null)?.confirmed === true
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  async function load() {
    if (!orderId) {
      setError('No order was specified.')
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      setOrder(await fetchOrder(orderId))
    } catch (e: unknown) {
      setOrder(null)
      setError(e instanceof Error ? e.message : 'Failed to load this order.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId])

  if (loading) {
    return (
      <section className="section-space">
        <div className="container-page">
          <div className="mx-auto max-w-4xl animate-pulse">
            <div className="h-5 w-32 rounded bg-sage-muted/50" />
            <div className="mt-6 h-10 w-2/3 rounded bg-sage-muted/50" />
            <div className="mt-8 h-64 rounded-2xl bg-sage-muted/50" />
          </div>
        </div>
      </section>
    )
  }

  if (error || !order) {
    return (
      <section className="section-space">
        <div className="container-page">
          <Card className="mx-auto max-w-2xl p-8 text-center">
            <p className="eyebrow">Order unavailable</p>
            <h1 className="mt-3 text-3xl md:text-4xl">We couldn’t load this order</h1>
            <p role="alert" className="mt-4 text-forest/75">{error || 'This order does not exist.'}</p>
            <div className="mt-6 flex flex-wrap justify-center gap-3">
              <Button type="button" variant="secondary" onClick={() => void load()}>
                <RefreshCw size={16} aria-hidden="true" /> Retry
              </Button>
              <ButtonLink to="/orders" variant="primary">Back to orders</ButtonLink>
            </div>
          </Card>
        </div>
      </section>
    )
  }

  const address = order.delivery_address

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-4xl">
          <Link to="/orders" className="inline-flex items-center gap-2 text-sm font-semibold text-forest hover:text-forest-dark">
            <ArrowLeft size={16} aria-hidden="true" /> Back to orders
          </Link>

          {confirmed ? (
            <div className="mt-6 flex items-start gap-3 rounded-2xl bg-sage-muted/50 p-5 text-forest-dark ring-1 ring-forest/10">
              <CheckCircle2 size={20} className="mt-0.5 shrink-0" aria-hidden="true" />
              <div>
                <p className="font-semibold">Order placed successfully</p>
                <p className="mt-1 text-sm text-forest/80">
                  Your order number is {order.order_number}. Payment is due on delivery.
                </p>
              </div>
            </div>
          ) : null}

          <div className="mt-6 flex flex-wrap items-start justify-between gap-4">
            <div>
              <p className="eyebrow">Order details</p>
              <h1 className="mt-3 text-4xl md:text-5xl">{order.order_number}</h1>
              <p className="mt-2 text-sm text-forest/70">Placed on {formatDate(order.placed_at)}</p>
            </div>
            <span className="rounded-full bg-sage-muted px-4 py-2 text-sm font-semibold text-forest-dark">
              {order.status_label}
            </span>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_320px]">
            <Card className="p-4 md:p-6">
              <h2 className="font-display text-2xl text-forest-dark">Items</h2>
              <ul className="mt-4 divide-y divide-forest/10">
                {order.items.map((item) => (
                  <li key={item.id} className="flex gap-4 py-4 first:pt-0 last:pb-0">
                    <ExternalImage
                      src={item.image_url || ''}
                      alt={item.product_name_snapshot}
                      className="h-20 w-20 rounded-2xl object-cover"
                      sizes="80px"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="font-semibold text-forest-dark">{item.product_name_snapshot}</p>
                      <p className="mt-1 text-sm text-forest/70">
                        {item.quantity} × {formatPrice(item.unit_price)} each
                      </p>
                    </div>
                    <p className="whitespace-nowrap font-semibold text-forest-dark">
                      {formatPrice(item.line_total)}
                    </p>
                  </li>
                ))}
              </ul>
            </Card>

            <div className="space-y-4 lg:sticky lg:top-28 lg:self-start">
              <Card className="p-5">
                <div className="flex items-center gap-2 text-forest-dark">
                  <MapPin size={18} aria-hidden="true" />
                  <h2 className="font-display text-xl">Delivery address</h2>
                </div>
                <p className="mt-4 font-semibold text-forest-dark">{address.recipient_name}</p>
                <p className="mt-1 text-sm text-forest/75">{address.phone}</p>
                <address className="mt-2 not-italic text-sm leading-relaxed text-forest/75">
                  {address.address_line1}
                  <br />
                  {address.address_line2 ? <>{address.address_line2}<br /></> : null}
                  {address.city} {address.postal_code}
                </address>

                <div className="mt-5 flex items-center gap-2 border-t border-forest/10 pt-4 text-forest-dark">
                  <Banknote size={18} aria-hidden="true" />
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-forest/55">Payment method</p>
                    <p className="mt-0.5 text-sm font-semibold">Cash on Delivery</p>
                  </div>
                </div>

                <div className="mt-5 flex justify-between gap-3 border-t border-forest/10 pt-4">
                  <span className="font-semibold text-forest-dark">Order total</span>
                  <span className="text-xl font-bold text-forest-dark">
                    {formatPrice(order.total_amount)}
                  </span>
                </div>
              </Card>
              <ButtonLink to="/shop" variant="secondary" className="w-full">
                Continue shopping
              </ButtonLink>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
