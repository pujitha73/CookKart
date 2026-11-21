import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, Package, RefreshCw } from 'lucide-react'
import { Button, ButtonLink } from '../../components/Button'
import { Card } from '../../components/Card'
import { formatPrice } from '../../services/catalogApi'
import { fetchOrders, type OrderSummary } from '../../services/orderApi'
import { useAuth } from '../auth/AuthContext'

type Props = {
  limit?: number
  showViewAll?: boolean
  title?: string
}

function formatDate(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })
}

export function OrderHistory({ limit, showViewAll = true, title = 'Order history' }: Props) {
  const { user } = useAuth()
  const [orders, setOrders] = useState<OrderSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!user) {
      setOrders([])
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const data = await fetchOrders()
      setOrders(limit ? data.slice(0, limit) : data)
    } catch (e: unknown) {
      setOrders([])
      setError(e instanceof Error ? e.message : 'Failed to load your orders.')
    } finally {
      setLoading(false)
    }
  }, [limit, user])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <section aria-label={title}>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-forest-dark">
          <Package size={18} aria-hidden="true" />
          <h2 className="font-display text-2xl">{title}</h2>
        </div>
        {showViewAll ? (
          <Link to="/orders" className="text-sm font-semibold text-forest underline decoration-lime/70 underline-offset-4 hover:text-forest-dark">
            View all orders
          </Link>
        ) : null}
      </div>

      {loading ? (
        <div className="space-y-3" aria-label="Loading orders">
          {Array.from({ length: 2 }).map((_, index) => (
            <div key={index} className="card-surface h-24 animate-pulse p-5" />
          ))}
        </div>
      ) : error ? (
        <Card className="p-6">
          <div className="flex items-start gap-3 text-red-800" role="alert">
            <AlertCircle size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
            <div>
              <p className="font-semibold">We couldn’t load your orders</p>
              <p className="mt-1 text-sm">{error}</p>
            </div>
          </div>
          <div className="mt-4">
            <Button type="button" variant="secondary" onClick={() => void load()}>
              <RefreshCw size={16} aria-hidden="true" /> Retry
            </Button>
          </div>
        </Card>
      ) : orders.length === 0 ? (
        <Card className="p-8 text-center">
          <p className="eyebrow">No orders yet</p>
          <p className="mt-3 text-forest/75">
            When you place a Cash on Delivery order, it will appear here.
          </p>
          <div className="mt-5">
            <ButtonLink to="/shop" variant="secondary">Browse the Shop</ButtonLink>
          </div>
        </Card>
      ) : (
        <ul className="space-y-3">
          {orders.map((order) => (
            <li key={order.id}>
              <Link
                to={`/orders/${order.id}`}
                className="card-surface block p-5 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-[var(--shadow-lift)]"
              >
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-forest-dark">{order.order_number}</p>
                    <p className="mt-1 text-sm text-forest/70">{formatDate(order.placed_at)}</p>
                  </div>
                  <span className="rounded-full bg-sage-muted px-3 py-1 text-xs font-semibold text-forest-dark">
                    {order.status_label}
                  </span>
                </div>
                <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-forest/10 pt-3">
                  <p className="text-sm text-forest/70">
                    {order.item_count} item{order.item_count === 1 ? '' : 's'} · Cash on Delivery
                  </p>
                  <p className="text-lg font-semibold text-forest-dark">{formatPrice(order.total_amount)}</p>
                </div>
                <p className="mt-2 text-sm font-semibold text-forest">View order details →</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
