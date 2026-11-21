import type { Product, ProductListResponse } from './catalogApi'
import { AuthenticationError } from './kitchenApi'
import { clearRequestCache } from './requestCache'
import type { Order, OrderSummary } from './orderApi'
import { supabase } from './supabaseClient'

export type AdminMe = {
  user_id: string
  email: string | null
  is_admin: boolean
}

export type AdminCatalogue = {
  total_products: number
  available_products: number
  unavailable_products: number
  total_categories: number
}

export type AdminDashboard = {
  total_orders: number
  awaiting_confirmation: number
  confirmed_orders: number
  cancelled_orders: number
  catalogue: AdminCatalogue
}

export type AdminOrderList = {
  items: OrderSummary[]
  total: number
  page: number
  page_size: number
  pages: number
}

/** Raised only when the backend has verified the user is not an administrator. */
export class AdminForbiddenError extends Error {
  constructor() {
    super('Administrator access required')
  }
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

  if (res.status === 403) throw new AdminForbiddenError()

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

export function fetchAdminMe(): Promise<AdminMe> {
  return request<AdminMe>('/api/admin/me')
}

export function fetchAdminDashboard(): Promise<AdminDashboard> {
  return request<AdminDashboard>('/api/admin/dashboard')
}

export function fetchAdminOrders(params: {
  page?: number
  page_size?: number
  search?: string
  status?: string
}): Promise<AdminOrderList> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.search) q.set('search', params.search)
  if (params.status) q.set('status', params.status)
  const qs = q.toString()
  return request<AdminOrderList>(`/api/admin/orders${qs ? `?${qs}` : ''}`)
}

export function fetchAdminOrder(orderId: string): Promise<Order> {
  return request<Order>(`/api/admin/orders/${encodeURIComponent(orderId)}`)
}

export function updateAdminOrderStatus(orderId: string, status: string): Promise<Order> {
  return request<Order>(`/api/admin/orders/${encodeURIComponent(orderId)}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  })
}

export function fetchAdminProducts(params: {
  page?: number
  page_size?: number
  search?: string
  availability?: string
}): Promise<ProductListResponse> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.search) q.set('search', params.search)
  if (params.availability && params.availability !== 'all') {
    q.set('availability', params.availability)
  }
  const qs = q.toString()
  return request<ProductListResponse>(`/api/admin/products${qs ? `?${qs}` : ''}`)
}

export async function updateAdminProductAvailability(productId: string, isAvailable: boolean): Promise<Product> {
  const product = await request<Product>(`/api/admin/products/${encodeURIComponent(productId)}/availability`, {
    method: 'PATCH',
    body: JSON.stringify({ is_available: isAvailable }),
  })
  // Public catalogue lists may be cached; drop them so shoppers see the change immediately.
  clearRequestCache()
  return product
}
