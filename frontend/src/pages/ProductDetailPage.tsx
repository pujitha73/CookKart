import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { ButtonLink } from '../components/Button'
import { Card } from '../components/Card'
import { ExternalImage } from '../components/ExternalImage'
import { ProductQuantityControl } from '../features/cart/ProductQuantityControl'
import { fetchProductBySlug, formatPrice, type Product } from '../services/catalogApi'
import { formatQuantity } from '../utils/formatQuantity'

export function ProductDetailPage() {
  const { slug } = useParams()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    let mounted = true
    setLoading(true)
    setError(null)
    fetchProductBySlug(slug)
      .then((data) => mounted && setProduct(data))
      .catch((e: unknown) => mounted && setError(e instanceof Error ? e.message : 'Failed to load product'))
      .finally(() => mounted && setLoading(false))
    return () => { mounted = false }
  }, [slug])

  if (loading) {
    return (
      <section className="section-space">
        <div className="container-page">
          <div className="mx-auto max-w-5xl animate-pulse">
            <div className="h-5 w-32 rounded bg-sage-muted/50" />
            <div className="mt-6 grid gap-8 lg:grid-cols-2">
              <div className="h-[380px] rounded-[1.25rem] bg-sage-muted/50" />
              <div className="space-y-4 pt-4">
                <div className="h-8 w-3/4 rounded bg-sage-muted/50" />
                <div className="h-5 w-1/3 rounded bg-sage-muted/50" />
                <div className="h-24 w-full rounded bg-sage-muted/50" />
              </div>
            </div>
          </div>
        </div>
      </section>
    )
  }

  if (error || !product) {
    return (
      <section className="section-space">
        <div className="container-page">
          <Card className="mx-auto max-w-2xl p-8 text-center">
            <p className="eyebrow">Product unavailable</p>
            <h1 className="mt-3 text-3xl md:text-4xl">We couldn’t load this product</h1>
            <p className="mt-4 text-forest/75">{error || 'The product may not exist or is no longer available.'}</p>
            <div className="mt-6 flex justify-center gap-3">
              <ButtonLink to="/shop" variant="primary"><ArrowLeft size={16} aria-hidden="true" /> Back to Shop</ButtonLink>
            </div>
          </Card>
        </div>
      </section>
    )
  }

  return (
    <section className="section-space">
      <div className="container-page">
        <div className="mx-auto max-w-5xl">
          <Link to="/shop" className="inline-flex items-center gap-2 text-sm font-semibold text-forest hover:text-forest-dark">
            <ArrowLeft size={16} aria-hidden="true" /> Back to Shop
          </Link>
          <div className="mt-6 grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
            <Card className="overflow-hidden p-3">
              <ExternalImage
                src={product.image_url || ''}
                alt={product.name}
                className="h-[340px] w-full rounded-[1rem] object-cover md:h-[460px]"
                priority
                sizes="(min-width: 1024px) 45vw, 100vw"
              />
            </Card>
            <div className="flex flex-col">
              {product.category ? (
                <p className="eyebrow">{product.category.name}</p>
              ) : (
                <p className="eyebrow">Product</p>
              )}
              <h1 className="mt-3 text-4xl md:text-5xl">{product.name}</h1>
              <p className="mt-4 text-2xl font-semibold text-forest-dark">{formatPrice(product.price)}</p>
              <p className="mt-1 text-sm text-forest/70">
                {formatQuantity(product.size, product.unit) || 'Available in shop catalogue'}
              </p>
              {product.description ? (
                <p className="mt-6 text-lg leading-relaxed text-forest/80">{product.description}</p>
              ) : (
                <p className="mt-6 text-lg leading-relaxed text-forest/70">Product details will appear here as catalogue information is enriched.</p>
              )}
              <div className="mt-8 rounded-2xl bg-sage-muted/40 p-5 ring-1 ring-forest/10">
                <p className="text-sm font-semibold text-forest-dark">Availability</p>
                <p className="mt-1 text-sm text-forest/80">
                  {product.is_available ? 'Currently available in the CookKart catalogue.' : 'Currently unavailable.'}
                </p>
              </div>
              <div className="mt-7">
                <ProductQuantityControl
                  productId={product.id}
                  productName={product.name}
                  disabled={!product.is_available}
                  fullWidth
                />
              </div>
              <p className="mt-4 text-xs leading-relaxed text-forest/60">
                Your cart is saved to your account. Proceed to checkout from your cart to place a Cash on Delivery order.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
