import { useCallback, useEffect, useState } from 'react'
import { ClipboardList, Package, ShoppingBag, Store } from 'lucide-react'
import { Link } from 'react-router-dom'
import { fetchAdminDashboard, type AdminDashboard } from '../../services/adminApi'
import { AdminError, AdminLoading, errorMessage } from '../../features/admin/AdminStates'

export function AdminDashboardPage() {
  const [data, setData] = useState<AdminDashboard | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetchAdminDashboard()
      .then(setData)
      .catch((cause: unknown) => setError(errorMessage(cause)))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { load() }, [load])

  if (loading) return <AdminLoading label="Loading dashboard…" />
  if (error) return <AdminError message={error} onRetry={load} />
  if (!data) return null

  const orderCards = [
    { label: 'Total orders', value: data.total_orders, hint: 'All recorded orders', icon: ShoppingBag },
    { label: 'Awaiting confirmation', value: data.awaiting_confirmation, hint: 'Status: placed', icon: ClipboardList },
    { label: 'Confirmed', value: data.confirmed_orders, hint: 'Status: confirmed', icon: Store },
    { label: 'Cancelled', value: data.cancelled_orders, hint: 'Status: cancelled', icon: Package },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {orderCards.map((card) => (
          <div key={card.label} className="card-surface p-5">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">{card.label}</p>
                <p className="mt-3 font-display text-4xl text-forest-dark">{card.value.toLocaleString('en-IN')}</p>
                <p className="mt-2 text-xs text-forest/60">{card.hint}</p>
              </div>
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-sage-muted text-forest">
                <card.icon size={18} aria-hidden="true" />
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <section className="card-surface p-6">
          <p className="eyebrow">Catalogue overview</p>
          <h2 className="mt-2 font-display text-2xl text-forest-dark">Products on CookKart</h2>
          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl bg-cream/70 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">Total products</p>
              <p className="mt-2 text-2xl font-semibold text-forest-dark">{data.catalogue.total_products}</p>
            </div>
            <div className="rounded-2xl bg-sage-muted/60 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">Available</p>
              <p className="mt-2 text-2xl font-semibold text-forest-dark">{data.catalogue.available_products}</p>
            </div>
            <div className="rounded-2xl bg-red-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-wider text-red-800/80">Unavailable</p>
              <p className="mt-2 text-2xl font-semibold text-red-800">{data.catalogue.unavailable_products}</p>
            </div>
          </div>
          <p className="mt-4 text-sm text-forest/70">
            Across {data.catalogue.total_categories} product {data.catalogue.total_categories === 1 ? 'category' : 'categories'}.
          </p>
        </section>

        <section className="card-surface p-6">
          <p className="eyebrow">Quick actions</p>
          <h2 className="mt-2 font-display text-2xl text-forest-dark">Continue working</h2>
          <div className="mt-5 space-y-3">
            <Link
              to="/admin/orders"
              className="flex items-center justify-between gap-3 rounded-2xl bg-cream/70 p-4 transition hover:bg-sage-muted/60"
            >
              <span>
                <span className="block font-semibold text-forest-dark">Review orders</span>
                <span className="mt-1 block text-xs text-forest/70">Search, filter and update order status</span>
              </span>
              <ShoppingBag size={18} className="shrink-0 text-forest" aria-hidden="true" />
            </Link>
            <Link
              to="/admin/products"
              className="flex items-center justify-between gap-3 rounded-2xl bg-cream/70 p-4 transition hover:bg-sage-muted/60"
            >
              <span>
                <span className="block font-semibold text-forest-dark">Product availability</span>
                <span className="mt-1 block text-xs text-forest/70">Enable or disable items in the shop</span>
              </span>
              <Package size={18} className="shrink-0 text-forest" aria-hidden="true" />
            </Link>
          </div>
        </section>
      </div>
    </div>
  )
}
