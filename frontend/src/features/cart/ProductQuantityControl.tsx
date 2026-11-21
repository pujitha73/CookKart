import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ShoppingCart } from 'lucide-react'
import { Button } from '../../components/Button'
import { QuantityStepper } from '../../components/QuantityStepper'
import { useAuth } from '../auth/AuthContext'
import { useCart } from './CartContext'

type Props = {
  productId: string
  productName: string
  disabled?: boolean
  fullWidth?: boolean
  compact?: boolean
}

export function ProductQuantityControl({ productId, productName, disabled = false, fullWidth, compact }: Props) {
  const { user } = useAuth()
  const { cart, loading: cartLoading, addProduct, changeQuantity, removeProduct } = useCart()
  const navigate = useNavigate()
  const location = useLocation()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setError(null)
  }, [productId])

  const item = cart?.items.find((entry) => entry.product.id === productId)
  const isBusy = busy || cartLoading

  async function handleAdd() {
    setError(null)
    if (!user) {
      navigate('/login', { state: { from: `${location.pathname}${location.search}` } })
      return
    }
    setBusy(true)
    try {
      await addProduct(productId)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to add this product to your cart.')
    } finally {
      setBusy(false)
    }
  }

  async function handleChange(next: number) {
    if (!item) return
    setError(null)
    setBusy(true)
    try {
      if (next < 1) await removeProduct(item.id)
      else await changeQuantity(item.id, next)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to update this product in your cart.')
    } finally {
      setBusy(false)
    }
  }

  if (disabled) {
    return (
      <div className={fullWidth ? 'w-full' : ''}>
        <Button type="button" variant="secondary" disabled className={fullWidth ? 'w-full' : ''}>
          Unavailable
        </Button>
      </div>
    )
  }

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {item ? (
        <div className={fullWidth ? 'flex w-full items-center justify-between gap-2' : 'flex items-center gap-2'}>
          <QuantityStepper
            value={item.quantity}
            onChange={(next) => void handleChange(next)}
            label={productName}
            disabled={isBusy}
            min={0}
            compact={compact}
          />
          <span className="text-xs font-semibold text-forest/60">
            {isBusy ? 'Updating…' : 'In cart'}
          </span>
        </div>
      ) : (
        <Button
          type="button"
          variant={user ? 'primary' : 'secondary'}
          onClick={() => void handleAdd()}
          disabled={isBusy}
          className={fullWidth ? 'w-full' : ''}
          aria-label={`Add ${productName} to cart`}
        >
          <ShoppingCart size={compact ? 14 : 16} aria-hidden="true" />
          {isBusy ? 'Adding…' : user ? 'Add to cart' : 'Log in to add'}
        </Button>
      )}
      {error ? (
        <p role="alert" className="mt-2 text-xs font-semibold text-red-700">
          {error}
        </p>
      ) : null}
    </div>
  )
}
