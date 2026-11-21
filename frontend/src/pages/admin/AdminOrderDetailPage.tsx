import { useCallback, useEffect, useState } from 'react'
import { ArrowLeft, MapPin, Package } from 'lucide-react'
import { useParams } from 'react-router-dom'
import { Button, ButtonLink } from '../../components/Button'
import { OrderStatusBadge } from '../../features/admin/AdminStatusBadge'
import { AdminError, AdminLoading, AdminSuccess, errorMessage } from '../../features/admin/AdminStates'
import { formatAdminDate, formatAdminMoney } from '../../features/admin/formatAdmin'
import { fetchAdminOrder, updateAdminOrderStatus } from '../../services/adminApi'
import type { Order } from '../../services/orderApi'

export function AdminOrderDetailPage() {
  const { orderId } = useParams<{ orderId: string }>()
  const [order, setOrder] = useState<Order | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [updating, setUpdating] = useState(false)

  const load = useCallback(() => {
    if (!orderId) return
    setLoading(true)
    setError(null)
    fetchAdminOrder(orderId)
      .then(setOrder)
      .catch((cause: unknown) => setError(errorMessage(cause)))
      .finally(() => setLoading(false))
  }, [orderId])

  useEffect(() => { load() }, [load])

  async function changeStatus(target: 'confirmed' | 'cancelled') {
    if (!orderId) return
    setUpdating(true)
    setActionError(null)
    setSuccess(null)
    try {
      const updated = await updateAdminOrderStatus(orderId, target)
      setOrder(updated)
      setSuccess(`Order ${updated.order_number} is now ${updated.status_label.toLowerCase()}.`)
    } catch (cause: unknown) {
      setActionError(errorMessage(cause))
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <AdminLoading label="Loading order…" />
  if (error) return <AdminError message={error} onRetry={load} />
  if (!order) return null

  const canConfirm = order.status === 'placed'
  const canCancel = order.status === 'placed' || order.status === 'confirmed'

  return (
    <div className="space-y-5">
      <ButtonLink to="/admin/orders" variant="ghost" size="md">
        <ArrowLeft size={16} aria-hidden="true" /> Back to orders
      </ButtonLink>

      {success ? <AdminSuccess message={success} /> : null}
      {actionError ? <AdminError message={actionError} /> : null}

      <section className="card-surface p-5 md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="eyebrow">Order detail</p>
            <h2 className="mt-2 font-display text-2xl text-forest-dark md:text-3xl">{order.order_number}</h2>
            <p className="mt-2 text-sm text-forest/70">Placed {formatAdminDate(order.placed_at)}</p>
          </div>
          <OrderStatusBadge status={order.status} label={order.status_label} />
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-2xl bg-cream/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">Order total</p>
            <p className="mt-2 text-xl font-semibold text-forest-dark">
              {formatAdminMoney(order.total_amount, order.currency)}
            </p>
          </div>
          <div className="rounded-2xl bg-cream/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">Items</p>
            <p className="mt-2 text-xl font-semibold text-forest-dark">{order.item_count}</p>
          </div>
          <div className="rounded-2xl bg-cream/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">Payment</p>
            <p className="mt-2 text-xl font-semibold uppercase text-forest-dark">{order.payment_method}</p>
          </div>
          <div className="rounded-2xl bg-cream/70 p-4">
            <p className="text-xs font-semibold uppercase tracking-wider text-forest/70">Currency</p>
            <p className="mt-2 text-xl font-semibold text-forest-dark">{order.currency}</p>
          </div>
        </div>

        {(canConfirm || canCancel) ? (
          <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-forest/10 pt-5">
            <p className="mr-auto text-sm text-forest/75">Update this order's status:</p>
            {canConfirm ? (
              <Button
                type="button"
                variant="primary"
                size="md"
                disabled={updating}
                onClick={() => changeStatus('confirmed')}
              >
                {updating ? 'Updating…' : 'Confirm order'}
              </Button>
            ) : null}
            {canCancel ? (
              <Button
                type="button"
                variant="ghost"
                size="md"
                disabled={updating}
                onClick={() => changeStatus('cancelled')}
              >
                {updating ? 'Updating…' : 'Cancel order'}
              </Button>
            ) : null}
          </div>
        ) : (
          <p className="mt-6 border-t border-forest/10 pt-5 text-sm text-forest/70">
            This order is cancelled. No further status changes are allowed.
          </p>
        )}
      </section>

      <div className="grid gap-5 lg:grid-cols-[1fr_1.4fr]">
        <section className="card-surface p-5 md:p-6">
          <div className="flex items-center gap-2">
            <MapPin size={18} className="text-forest" aria-hidden="true" />
            <h3 className="font-display text-xl text-forest-dark">Delivery information</h3>
          </div>
          <dl className="mt-4 space-y-3 text-sm">
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wider text-forest/70">Recipient</dt>
              <dd className="mt-1 text-forest-dark">{order.delivery_address.recipient_name}</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wider text-forest/70">Phone</dt>
              <dd className="mt-1 text-forest-dark">{order.delivery_address.phone}</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wider text-forest/70">Address</dt>
              <dd className="mt-1 whitespace-pre-line text-forest-dark">
                {order.delivery_address.address_line1}
                {order.delivery_address.address_line2 ? `\n${order.delivery_address.address_line2}` : ''}
                {`\n${order.delivery_address.city} ${order.delivery_address.postal_code}`}
              </dd>
            </div>
          </dl>
        </section>

        <section className="card-surface p-5 md:p-6">
          <div className="flex items-center gap-2">
            <Package size={18} className="text-forest" aria-hidden="true" />
            <h3 className="font-display text-xl text-forest-dark">Purchased items</h3>
          </div>
          <div className="mt-4 overflow-x-auto rounded-2xl ring-1 ring-forest/10">
            <table className="w-full min-w-[480px] border-collapse text-left text-sm">
              <thead className="bg-cream/80 text-xs uppercase tracking-wider text-forest/70">
                <tr>
                  <th className="px-3 py-3 font-semibold">Product</th>
                  <th className="px-3 py-3 font-semibold">Qty</th>
                  <th className="px-3 py-3 font-semibold">Unit price</th>
                  <th className="px-3 py-3 font-semibold">Line total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-forest/10 bg-white/60">
                {order.items.map((item) => (
                  <tr key={item.id}>
                    <td className="px-3 py-3 text-forest-dark">
                      <span className="block font-semibold">{item.product_name_snapshot}</span>
                      {(item.size || item.unit) ? (
                        <span className="mt-1 block text-xs text-forest/60">
                          {[item.size, item.unit].filter(Boolean).join(' · ')}
                        </span>
                      ) : null}
                    </td>
                    <td className="px-3 py-3 text-forest/80">{item.quantity}</td>
                    <td className="px-3 py-3 text-forest/80">{formatAdminMoney(item.unit_price, order.currency)}</td>
                    <td className="px-3 py-3 font-semibold text-forest-dark">
                      {formatAdminMoney(item.line_total, order.currency)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4 flex justify-end gap-6 text-sm">
            <span className="text-forest/70">Order total</span>
            <span className="font-semibold text-forest-dark">{formatAdminMoney(order.total_amount, order.currency)}</span>
          </div>
        </section>
      </div>
    </div>
  )
}
