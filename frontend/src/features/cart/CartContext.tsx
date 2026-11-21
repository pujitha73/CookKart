import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { useAuth } from '../auth/AuthContext'
import { AuthenticationError } from '../../services/kitchenApi'
import {
  addCartItem,
  fetchCart,
  removeCartItem,
  updateCartItem,
  type Cart,
} from '../../services/cartApi'

type CartContextValue = {
  cart: Cart | null
  itemCount: number
  loading: boolean
  error: string | null
  refreshCart: () => Promise<void>
  addProduct: (productId: string, quantity?: number) => Promise<void>
  changeQuantity: (itemId: string, quantity: number) => Promise<void>
  removeProduct: (itemId: string) => Promise<void>
  replaceCart: (cart: Cart) => void
}

const CartContext = createContext<CartContextValue | undefined>(undefined)

function messageFor(error: unknown, fallback: string, signOut: () => Promise<unknown>): string {
  if (error instanceof AuthenticationError) {
    void signOut()
    return error.message
  }
  return error instanceof Error && error.message.trim() ? error.message : fallback
}

export function CartProvider({ children }: { children: ReactNode }) {
  const { user, signOut } = useAuth()
  const userId = user?.id
  const [cart, setCart] = useState<Cart | null>(null)
  const [itemCount, setItemCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const applyCart = useCallback((next: Cart) => {
    setCart(next)
    setItemCount(next.item_count)
    setError(null)
  }, [])

  const refreshCart = useCallback(async () => {
    if (!userId) {
      setCart(null)
      setItemCount(0)
      setError(null)
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      applyCart(await fetchCart())
    } catch (e: unknown) {
      setCart(null)
      setItemCount(0)
      setError(messageFor(e, 'Failed to load your cart.', signOut))
    } finally {
      setLoading(false)
    }
  }, [applyCart, signOut, userId])

  useEffect(() => {
    void refreshCart()
  }, [refreshCart])

  const addProduct = useCallback(
    async (productId: string, quantity = 1) => {
      try {
        await addCartItem(productId, quantity)
        applyCart(await fetchCart())
      } catch (e: unknown) {
        const message = messageFor(e, 'Failed to add this product to your cart.', signOut)
        setError(message)
        throw new Error(message)
      }
    },
    [applyCart, signOut],
  )

  const changeQuantity = useCallback(
    async (itemId: string, quantity: number) => {
      try {
        await updateCartItem(itemId, quantity)
        applyCart(await fetchCart())
      } catch (e: unknown) {
        const message = messageFor(e, 'Failed to update this cart item.', signOut)
        setError(message)
        throw new Error(message)
      }
    },
    [applyCart, signOut],
  )

  const removeProduct = useCallback(
    async (itemId: string) => {
      try {
        await removeCartItem(itemId)
        applyCart(await fetchCart())
      } catch (e: unknown) {
        const message = messageFor(e, 'Failed to remove this cart item.', signOut)
        setError(message)
        throw new Error(message)
      }
    },
    [applyCart, signOut],
  )

  const value = useMemo<CartContextValue>(
    () => ({
      cart,
      itemCount,
      loading,
      error,
      refreshCart,
      addProduct,
      changeQuantity,
      removeProduct,
      replaceCart: applyCart,
    }),
    [
      addProduct,
      applyCart,
      cart,
      changeQuantity,
      error,
      itemCount,
      loading,
      refreshCart,
      removeProduct,
    ],
  )

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export function useCart() {
  const ctx = useContext(CartContext)
  if (!ctx) throw new Error('useCart must be used within CartProvider')
  return ctx
}
