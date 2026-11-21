import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ShoppingCart } from 'lucide-react'
import { Button } from '../../components/Button'
import { useAuth } from '../auth/AuthContext'
import { useCart } from './CartContext'

type Props = {
  productId: string
  productName: string
  disabled?: boolean
  fullWidth?: boolean
  compact?: boolean
}

type Status = { kind: 'success' | 'error'; text: string }

export function AddToCartButton({ productId, productName, disabled = false, fullWidth, compact }: Props) {
  const { user } = useAuth()
  const { addProduct } = useCart()
  const navigate = useNavigate()
  const location = useLocation()
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState<Status | null>(null)

  useEffect(() => {
    setStatus(null)
  }, [productId])

  async function handleAdd() {
    setStatus(null)
    if (!user) {
      navigate('/login', { state: { from: `${location.pathname}${location.search}` } })
      return
    }

    setBusy(true)
    try {
      await addProduct(productId)
      setStatus({ kind: 'success', text: `Added ${productName} to your cart.` })
    } catch (e: unknown) {
      setStatus({
        kind: 'error',
        text: e instanceof Error ? e.message : 'Failed to add this product to your cart.',
      })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className={fullWidth ? 'w-full' : ''}>
      <Button
        type="button"
        variant={user ? 'primary' : 'secondary'}
        onClick={handleAdd}
        disabled={disabled || busy}
        className={fullWidth ? 'w-full' : ''}
        aria-label={`Add ${productName} to cart`}
      >
        <ShoppingCart size={compact ? 14 : 16} aria-hidden="true" />
        {disabled ? 'Unavailable' : busy ? 'Adding…' : user ? 'Add to cart' : 'Log in to add'}
      </Button>
      {status ? (
        <p
          role={status.kind === 'error' ? 'alert' : 'status'}
          className={`mt-2 text-xs font-semibold ${status.kind === 'error' ? 'text-red-700' : 'text-forest'}`}
        >
          {status.text}
        </p>
      ) : null}
    </div>
  )
}
