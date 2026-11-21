import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { ChevronLeft, ChevronRight, Eye, Search } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { Button } from '../../components/Button'
import { OrderStatusBadge } from '../../features/admin/AdminStatusBadge'
import { AdminEmpty, AdminError, AdminLoading, AdminSuccess, errorMessage } from '../../features/admin/AdminStates'
import { formatAdminDate, formatAdminMoney } from '../../features/admin/formatAdmin'
import { fetchAdminOrders, type AdminOrderList } from '../../services/adminApi'

const statusOptions = [
  { value: '', label: 'All statuses' },
  { value: 'placed', label: 'Awaiting confirmation' },
  { value: 'confirmed', label: 'Confirmed' },
  { value: 'cancelled', label: 'Cancelled' },
]

const inputClass =
  'w-full rounded-2xl border border-forest/15 bg-white px-4 py-2.5 text-sm text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0'

export function AdminOrdersPage() {
  const location = useLocation()
  const [notice] = useState<string | null>(
    () => (location.state as { success?: string } | null)?.success ?? null,
  )
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<AdminOrderList | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetchAdminOrders({ page, page_size: 20, search, status })
      .then(setData)
      .catch((cause: unknown) => setError(errorMessage(cause)))
      .finally(() => setLoading(false))
  }, [page, search, status])

  useEffect(() => { load() }, [load])

  function applySearch(event: FormEvent) {
    event.preventDefault()
    setPage(1)
    setSearch(searchInput.trim())
  }

  function clearFilters() {
    setSearchInput('')
    setSearch('')
    setStatus('')
    setPage(1)
  }

  return (
    <section className="card-surface overflow-hidden">
      <div className="border-b border-forest/10 p-5 md:p-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="eyebrow">Order management</p>
            <h2 className="mt-2 font-display text-2xl text-forest-dark">Customer orders</h2>
            <p className="mt-1 text-sm text-forest/70">
              {data ? `${data.total} order${data.total === 1 ? '' : 's'} found` : 'Search and review all orders'}
            </p>
          </div>
        </div>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-end">
          <form onSubmit={applySearch} className="flex flex-1 flex-col gap-2 sm:flex-row">
            <label className="flex-1">
              <span className="mb-1.5 block text-xs font-semibold text-forest/80">Search by order number</span>
              <span className="relative block">
                <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-forest/50" aria-hidden="true" />
                <input
                  type="search"
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="CK-20261117-AB12CD"
                  className={`${inputClass} pl-9`}
                />
              </span>
            </label>
            <Button type="submit" variant="primary" size="md">Search</Button>
          </form>
          <label className="sm:w-56">
            <span className="mb-1.5 block text-xs font-semibold text-forest/80">Status filter</span>
            <select
              value={status}
              onChange={(event) => { setStatus(event.target.value); setPage(1) }}
              className={inputClass}
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
          </label>
          <Button type="button" variant="ghost" size="md" onClick={clearFilters}>Clear</Button>
        </div>
      </div>

      <div className="p-5 md:p-6">
        {notice ? <AdminSuccess message={notice} /> : null}
        {loading ? <AdminLoading label="Loading orders…" /> : null}
        {!loading && error ? <AdminError message={error} onRetry={load} /> : null}
        {!loading && !error && data && data.items.length === 0 ? (
          <AdminEmpty
            title="No orders found"
            description="Try a different order number or clear the status filter."
          />
        ) : null}

        {!loading && !error && data && data.items.length > 0 ? (
          <>
            <div className="overflow-x-auto rounded-2xl ring-1 ring-forest/10">
              <table className="w-full min-w-[720px] border-collapse text-left text-sm">
                <thead className="bg-cream/80 text-xs uppercase tracking-wider text-forest/70">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Order</th>
                    <th className="px-4 py-3 font-semibold">Placed</th>
                    <th className="px-4 py-3 font-semibold">Status</th>
                    <th className="px-4 py-3 font-semibold">Items</th>
                    <th className="px-4 py-3 font-semibold">Total</th>
                    <th className="px-4 py-3 font-semibold">Payment</th>
                    <th className="px-4 py-3 font-semibold"><span className="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-forest/10 bg-white/60">
                  {data.items.map((order) => (
                    <tr key={order.id} className="transition hover:bg-sage-muted/30">
                      <td className="px-4 py-3 font-semibold text-forest-dark">{order.order_number}</td>
                      <td className="px-4 py-3 text-forest/80">{formatAdminDate(order.placed_at)}</td>
                      <td className="px-4 py-3"><OrderStatusBadge status={order.status} label={order.status_label} /></td>
                      <td className="px-4 py-3 text-forest/80">{order.item_count}</td>
                      <td className="px-4 py-3 font-semibold text-forest-dark">
                        {formatAdminMoney(order.total_amount, order.currency)}
                      </td>
                      <td className="px-4 py-3 uppercase text-forest/70">{order.payment_method}</td>
                      <td className="px-4 py-3 text-right">
                        <Link
                          to={`/admin/orders/${order.id}`}
                          state={{ fromAdminList: true }}
                          className="inline-flex items-center gap-1 rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-forest ring-1 ring-forest/15 hover:bg-sage-muted/60"
                        >
                          <Eye size={14} aria-hidden="true" /> View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="mt-5 flex flex-wrap items-center justify-between gap-3 text-sm text-forest/75">
              <p>
                Page {data.page} of {data.pages || 1} · showing {data.items.length} of {data.total}
              </p>
              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="ghost"
                  size="md"
                  disabled={page <= 1}
                  onClick={() => setPage((value) => Math.max(1, value - 1))}
                >
                  <ChevronLeft size={16} aria-hidden="true" /> Previous
                </Button>
                <Button
                  type="button"
                  variant="ghost"
                  size="md"
                  disabled={page >= data.pages}
                  onClick={() => setPage((value) => value + 1)}
                >
                  Next <ChevronRight size={16} aria-hidden="true" />
                </Button>
              </div>
            </div>
          </>
        ) : null}
      </div>
    </section>
  )
}
