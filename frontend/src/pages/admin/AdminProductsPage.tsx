import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { ChevronLeft, ChevronRight, Search } from 'lucide-react'
import { Button } from '../../components/Button'
import { AvailabilityBadge } from '../../features/admin/AdminStatusBadge'
import { AdminEmpty, AdminError, AdminLoading, AdminSuccess, errorMessage } from '../../features/admin/AdminStates'
import { fetchAdminProducts, updateAdminProductAvailability } from '../../services/adminApi'
import { formatPrice, type ProductListResponse } from '../../services/catalogApi'

const inputClass =
  'w-full rounded-2xl border border-forest/15 bg-white px-4 py-2.5 text-sm text-forest placeholder:text-forest/40 focus:border-lime focus:ring-0'

export function AdminProductsPage() {
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')
  const [availability, setAvailability] = useState('all')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<ProductListResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoading(true)
    setError(null)
    fetchAdminProducts({ page, page_size: 20, search, availability })
      .then(setData)
      .catch((cause: unknown) => setError(errorMessage(cause)))
      .finally(() => setLoading(false))
  }, [page, search, availability])

  useEffect(() => { load() }, [load])

  function applySearch(event: FormEvent) {
    event.preventDefault()
    setPage(1)
    setSearch(searchInput.trim())
  }

  function clearFilters() {
    setSearchInput('')
    setSearch('')
    setAvailability('all')
    setPage(1)
  }

  async function toggle(productId: string, nextAvailable: boolean) {
    setBusyId(productId)
    setActionError(null)
    setSuccess(null)
    try {
      const updated = await updateAdminProductAvailability(productId, nextAvailable)
      setSuccess(`${updated.name} is now ${updated.is_available ? 'available' : 'unavailable'} to customers.`)
      load()
    } catch (cause: unknown) {
      setActionError(errorMessage(cause))
    } finally {
      setBusyId(null)
    }
  }

  return (
    <section className="card-surface overflow-hidden">
      <div className="border-b border-forest/10 p-5 md:p-6">
        <p className="eyebrow">Catalogue management</p>
        <h2 className="mt-2 font-display text-2xl text-forest-dark">Product availability</h2>
        <p className="mt-1 text-sm text-forest/70">
          {data ? `${data.total} product${data.total === 1 ? '' : 's'} found` : 'Browse and enable or disable existing products'}
        </p>

        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-end">
          <form onSubmit={applySearch} className="flex flex-1 flex-col gap-2 sm:flex-row">
            <label className="flex-1">
              <span className="mb-1.5 block text-xs font-semibold text-forest/80">Search by product name</span>
              <span className="relative block">
                <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-forest/50" aria-hidden="true" />
                <input
                  type="search"
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder="e.g. rice"
                  className={`${inputClass} pl-9`}
                />
              </span>
            </label>
            <Button type="submit" variant="primary" size="md">Search</Button>
          </form>
          <label className="sm:w-52">
            <span className="mb-1.5 block text-xs font-semibold text-forest/80">Availability</span>
            <select
              value={availability}
              onChange={(event) => { setAvailability(event.target.value); setPage(1) }}
              className={inputClass}
            >
              <option value="all">All products</option>
              <option value="available">Available</option>
              <option value="unavailable">Unavailable</option>
            </select>
          </label>
          <Button type="button" variant="ghost" size="md" onClick={clearFilters}>Clear</Button>
        </div>
      </div>

      <div className="p-5 md:p-6">
        {success ? <AdminSuccess message={success} /> : null}
        {actionError ? <AdminError message={actionError} /> : null}
        {loading ? <AdminLoading label="Loading products…" /> : null}
        {!loading && error ? <AdminError message={error} onRetry={load} /> : null}
        {!loading && !error && data && data.items.length === 0 ? (
          <AdminEmpty
            title="No products found"
            description="Try a different name or clear the availability filter."
          />
        ) : null}

        {!loading && !error && data && data.items.length > 0 ? (
          <>
            <div className="overflow-x-auto rounded-2xl ring-1 ring-forest/10">
              <table className="w-full min-w-[640px] border-collapse text-left text-sm">
                <thead className="bg-cream/80 text-xs uppercase tracking-wider text-forest/70">
                  <tr>
                    <th className="px-4 py-3 font-semibold">Product</th>
                    <th className="px-4 py-3 font-semibold">Category</th>
                    <th className="px-4 py-3 font-semibold">Price</th>
                    <th className="px-4 py-3 font-semibold">Availability</th>
                    <th className="px-4 py-3 font-semibold text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-forest/10 bg-white/60">
                  {data.items.map((product) => (
                    <tr key={product.id} className="transition hover:bg-sage-muted/30">
                      <td className="px-4 py-3">
                        <span className="block font-semibold text-forest-dark">{product.name}</span>
                        {(product.size || product.unit) ? (
                          <span className="mt-1 block text-xs text-forest/60">
                            {[product.size, product.unit].filter(Boolean).join(' · ')}
                          </span>
                        ) : null}
                      </td>
                      <td className="px-4 py-3 text-forest/80">{product.category?.name ?? '—'}</td>
                      <td className="px-4 py-3 font-semibold text-forest-dark">{formatPrice(product.price)}</td>
                      <td className="px-4 py-3"><AvailabilityBadge available={product.is_available} /></td>
                      <td className="px-4 py-3 text-right">
                        <Button
                          type="button"
                          variant={product.is_available ? 'ghost' : 'secondary'}
                          size="md"
                          disabled={busyId === product.id}
                          onClick={() => toggle(product.id, !product.is_available)}
                        >
                          {busyId === product.id ? 'Saving…' : product.is_available ? 'Disable' : 'Enable'}
                        </Button>
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
