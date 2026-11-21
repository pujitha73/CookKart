import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { Search, SlidersHorizontal } from 'lucide-react'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import { Button } from '../components/Button'
import { ProductQuantityControl } from '../features/cart/ProductQuantityControl'
import { fetchCategories, fetchProducts, formatPrice, type Category, type Product } from '../services/catalogApi'
import { formatQuantity } from '../utils/formatQuantity'

export function ShopPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [categories, setCategories] = useState<Category[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [total, setTotal] = useState(0)
  const [pages, setPages] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const page = Math.max(1, Number(searchParams.get('page') || '1'))
  const category = searchParams.get('category') || ''
  const search = searchParams.get('q') || ''
  const [searchInput, setSearchInput] = useState(search)

  useEffect(() => {
    setSearchInput(search)
  }, [search])

  useEffect(() => {
    let mounted = true
    fetchCategories()
      .then((data) => mounted && setCategories(data))
      .catch(() => mounted && setCategories([]))
    return () => { mounted = false }
  }, [])

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    fetchProducts({ page, page_size: 12, category: category || undefined, search: search || undefined })
      .then((data) => {
        if (!mounted) return
        setProducts(data.items)
        setTotal(data.total)
        setPages(data.pages)
      })
      .catch((e: unknown) => {
        if (!mounted) return
        setError(e instanceof Error ? e.message : 'Failed to load products')
        setProducts([])
        setTotal(0)
        setPages(0)
      })
      .finally(() => mounted && setLoading(false))
    return () => { mounted = false }
  }, [page, category, search])

  const activeCategoryName = useMemo(
    () => categories.find((c) => c.slug === category)?.name,
    [categories, category],
  )

  function updateParams(next: { page?: number; category?: string; q?: string }) {
    const p = new URLSearchParams(searchParams)
    if (next.category !== undefined) {
      if (next.category) p.set('category', next.category); else p.delete('category')
      p.set('page', '1')
    }
    if (next.q !== undefined) {
      if (next.q) p.set('q', next.q); else p.delete('q')
      p.set('page', '1')
    }
    if (next.page !== undefined) p.set('page', String(next.page))
    setSearchParams(p)
  }

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mb-8 md:mb-10">
          <p className="eyebrow">Shop</p>
          <h1 className="mt-3 text-4xl md:text-5xl">Fresh groceries, thoughtfully presented</h1>
          <p className="mt-4 max-w-2xl text-lg leading-relaxed text-forest/80">
            Browse available products from the CookKart catalogue. Filter by category or search by name to find what you need.
          </p>
        </div>

        <div className="grid gap-8 lg:grid-cols-[280px_1fr]">
          <aside className="space-y-4 lg:sticky lg:top-28 lg:self-start">
            <Card className="p-5">
              <div className="mb-3 flex items-center gap-2 text-forest-dark">
                <SlidersHorizontal size={18} aria-hidden="true" />
                <h2 className="font-display text-xl">Categories</h2>
              </div>
              <div className="flex flex-col gap-2">
                <button
                  type="button"
                  onClick={() => updateParams({ category: '' })}
                  className={`rounded-xl px-3 py-2 text-left text-sm font-semibold transition ${!category ? 'bg-sage-muted text-forest-dark' : 'text-forest hover:bg-cream'}`}
                >
                  All products
                </button>
                {categories.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => updateParams({ category: c.slug })}
                    className={`rounded-xl px-3 py-2 text-left text-sm font-semibold transition ${category === c.slug ? 'bg-sage-muted text-forest-dark' : 'text-forest hover:bg-cream'}`}
                  >
                    {c.name}
                  </button>
                ))}
                {!categories.length && !loading ? (
                  <p className="px-1 text-sm text-forest/60">No categories available yet.</p>
                ) : null}
              </div>
            </Card>
          </aside>

          <div>
            <Card className="mb-6 p-4 md:p-5">
              <form
                className="flex flex-col gap-3 sm:flex-row"
                onSubmit={(e) => { e.preventDefault(); updateParams({ q: searchInput.trim() }) }}
              >
                <label className="relative block flex-1">
                  <span className="sr-only">Search products by name</span>
                  <Search size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-forest/45" aria-hidden="true" />
                  <input
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    type="search"
                    placeholder="Search products by name"
                    className="w-full rounded-full border border-forest/15 bg-white py-3 pl-10 pr-4 text-forest placeholder:text-forest/40 focus:border-lime"
                  />
                </label>
                <Button type="submit" variant="primary">Search</Button>
                {(search || category) ? (
                  <Button type="button" variant="ghost" onClick={() => { setSearchInput(''); setSearchParams(new URLSearchParams()) }}>Clear</Button>
                ) : null}
              </form>
              <div className="mt-3 text-sm text-forest/70">
                {activeCategoryName ? <span>Category: <strong className="text-forest-dark">{activeCategoryName}</strong> · </span> : null}
                {search ? <span>Search: <strong className="text-forest-dark">“{search}”</strong> · </span> : null}
                <span>{loading ? 'Loading…' : `${total} product${total === 1 ? '' : 's'}`}</span>
              </div>
            </Card>

            {loading ? (
              <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} className="card-surface animate-pulse p-4">
                    <div className="h-44 rounded-2xl bg-sage-muted/50" />
                    <div className="mt-4 h-4 w-2/3 rounded bg-sage-muted/50" />
                    <div className="mt-2 h-4 w-1/3 rounded bg-sage-muted/50" />
                  </div>
                ))}
              </div>
            ) : error ? (
              <Card className="p-8 text-center">
                <p className="eyebrow">Unable to load products</p>
                <p className="mt-3 text-lg text-forest-dark">{error}</p>
                <p className="mt-2 text-sm text-forest/70">Please ensure the backend API is running and try again.</p>
                <div className="mt-5"><Button variant="primary" onClick={() => window.location.reload()}>Retry</Button></div>
              </Card>
            ) : products.length === 0 ? (
              <Card className="p-10 text-center">
                <p className="eyebrow">No products found</p>
                <h2 className="mt-3 text-3xl">We couldn’t find matching products</h2>
                <p className="mt-3 text-forest/75">
                  {search || category
                    ? 'Try adjusting your search or category filters.'
                    : 'The catalogue is currently empty. Products will appear here once they are available in the database.'}
                </p>
              </Card>
            ) : (
              <>
                <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
                  {products.map((p) => (
                    <Card key={p.id} className="group h-full overflow-hidden p-3 transition-all duration-300 hover:-translate-y-1 hover:shadow-[var(--shadow-lift)]">
                      <Link to={`/shop/${p.slug}`} className="block">
                        <ExternalImage
                          src={p.image_url || ''}
                          alt={p.name}
                          className="h-44 w-full rounded-[1rem] object-cover"
                          sizes="(min-width: 1280px) 20vw, (min-width: 640px) 40vw, 100vw"
                        />
                        <div className="p-2 pt-4">
                          {p.category?.name ? <p className="text-xs font-semibold uppercase tracking-[0.14em] text-forest/60">{p.category.name}</p> : null}
                          <h3 className="mt-1 text-xl text-forest-dark">{p.name}</h3>
                          {p.description ? <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-forest/75">{p.description}</p> : null}
                          <div className="mt-4 flex items-center justify-between gap-3">
                            <p className="text-lg font-semibold text-forest-dark">{formatPrice(p.price)}</p>
                            <span className="text-xs font-semibold text-forest/60">{formatQuantity(p.size, p.unit)}</span>
                          </div>
                        </div>
                      </Link>
                      <div className="px-2 pb-2 pt-3">
                        <ProductQuantityControl
                          productId={p.id}
                          productName={p.name}
                          disabled={!p.is_available}
                          fullWidth
                          compact
                        />
                      </div>
                    </Card>
                  ))}
                </div>

                {pages > 1 ? (
                  <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                    <Button variant="ghost" disabled={page <= 1} onClick={() => updateParams({ page: page - 1 })}>Previous</Button>
                    <span className="px-3 text-sm font-semibold text-forest/75">Page {page} of {pages}</span>
                    <Button variant="ghost" disabled={page >= pages} onClick={() => updateParams({ page: page + 1 })}>Next</Button>
                  </div>
                ) : null}
              </>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
