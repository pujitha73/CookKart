import type { Product } from './catalogApi'
import { AuthenticationError } from './kitchenApi'
import { supabase } from './supabaseClient'

export type CartItem = {
  id: string
  product: Product
  quantity: number
  unit_price: string | number
  subtotal: string | number
  created_at?: string
  updated_at?: string
}

export type Cart = {
  items: CartItem[]
  item_count: number
  line_count: number
  total: string | number
  unavailable_item_count: number
}

export type MissingProduct = {
  id: string
  name: string
  slug: string
  price: string | number
  unit?: string | null
  size?: string | null
  image_url?: string | null
  match_priority: number
  substitution_note?: string | null
  cart_quantity: number
}

export type MissingIngredient = {
  id: string
  name: string
  quantity?: string | null
  unit?: string | null
  preparation_note?: string | null
  display_order: number
  status: 'available' | 'unmapped' | 'unavailable'
  products: MissingProduct[]
}

export type RecipeCartPlan = {
  recipe: {
    id: string
    name: string
    slug: string
    image_url?: string | null
  }
  missing_ingredients: MissingIngredient[]
  required_count: number
  available_pantry_count: number
  missing_count: number
  matched_missing_count: number
  unmapped_missing_count: number
  unavailable_missing_count: number
  default_cart_quantity: number
  quantity_note: string
}

export type RecipeCartAddResult = {
  cart: Cart
  products_added: number
  added_product_ids: string[]
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''

async function accessToken(): Promise<string> {
  if (!supabase) throw new AuthenticationError('Supabase is not configured.')
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (!token) throw new AuthenticationError()
  return token
}

async function request<T>(path: string, init: RequestInit = {}, allowRefresh = true): Promise<T> {
  const token = await accessToken()
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...init.headers,
    },
  })

  if (res.status === 401 && allowRefresh && supabase) {
    const { data, error } = await supabase.auth.refreshSession()
    if (!error && data.session?.access_token) return request<T>(path, init, false)
    throw new AuthenticationError()
  }

  if (!res.ok) {
    let payload: unknown = null
    try {
      payload = await res.json()
    } catch {
      // ignore non-JSON error bodies
    }
    const detail =
      payload && typeof payload === 'object' && 'detail' in payload
        ? (payload as { detail?: unknown }).detail
        : null
    throw new Error(typeof detail === 'string' && detail.trim() ? detail : `Request failed (${res.status})`)
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export function fetchCart(): Promise<Cart> {
  return request<Cart>('/api/cart')
}

export function addCartItem(productId: string, quantity = 1): Promise<CartItem> {
  return request<CartItem>('/api/cart/items', {
    method: 'POST',
    body: JSON.stringify({ product_id: productId, quantity }),
  })
}

export function updateCartItem(itemId: string, quantity: number): Promise<CartItem> {
  return request<CartItem>(`/api/cart/items/${encodeURIComponent(itemId)}`, {
    method: 'PATCH',
    body: JSON.stringify({ quantity }),
  })
}

export function removeCartItem(itemId: string): Promise<void> {
  return request<void>(`/api/cart/items/${encodeURIComponent(itemId)}`, {
    method: 'DELETE',
  })
}

export function fetchRecipeCartPlan(slug: string): Promise<RecipeCartPlan> {
  return request<RecipeCartPlan>(`/api/cart/recipes/${encodeURIComponent(slug)}/plan`)
}

export function addSelectedRecipeProducts(
  slug: string,
  productIds: string[],
): Promise<RecipeCartAddResult> {
  return request<RecipeCartAddResult>(
    `/api/cart/recipes/${encodeURIComponent(slug)}/add-selected`,
    {
      method: 'POST',
      body: JSON.stringify({ product_ids: productIds }),
    },
  )
}
