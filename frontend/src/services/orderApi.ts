import { AuthenticationError } from './kitchenApi'
import { supabase } from './supabaseClient'

export type DeliveryAddress = {
  recipient_name: string
  phone: string
  address_line1: string
  address_line2?: string | null
  city: string
  postal_code: string
}

export type OrderItem = {
  id: string
  product_id: string | null
  product_name_snapshot: string
  quantity: number
  unit_price: string | number
  line_total: string | number
  image_url?: string | null
  size?: string | null
  unit?: string | null
}

export type OrderSummary = {
  id: string
  order_number: string
  status: string
  status_label: string
  total_amount: string | number
  currency: string
  placed_at: string
  item_count: number
  payment_method: string
}

export type Order = OrderSummary & {
  delivery_address: DeliveryAddress
  items: OrderItem[]
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

  return res.json() as Promise<T>
}

export function placeOrder(address: DeliveryAddress): Promise<Order> {
  return request<Order>('/api/orders', {
    method: 'POST',
    body: JSON.stringify({ delivery_address: address }),
  })
}

export function fetchOrders(): Promise<OrderSummary[]> {
  return request<OrderSummary[]>('/api/orders')
}

export function fetchOrder(orderId: string): Promise<Order> {
  return request<Order>(`/api/orders/${encodeURIComponent(orderId)}`)
}
