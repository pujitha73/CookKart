import { cachedRequest } from './requestCache'

export type Category = {
  id: string
  name: string
  slug: string
  description?: string | null
}

export type Product = {
  id: string
  category_id: string
  name: string
  slug: string
  description?: string | null
  price: string | number
  unit?: string | null
  size?: string | null
  image_url?: string | null
  is_available: boolean
  category?: Category | null
}

export type ProductListResponse = {
  items: Product[]
  total: number
  page: number
  page_size: number
  pages: number
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: 'application/json' },
  })
  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (data?.detail) message = typeof data.detail === 'string' ? data.detail : message
    } catch {
      // ignore
    }
    throw new Error(message)
  }
  return res.json() as Promise<T>
}

export function fetchCategories(): Promise<Category[]> {
  return cachedRequest('catalog:categories', () => request<Category[]>('/api/catalog/categories'))
}

export function fetchProducts(params: {
  page?: number
  page_size?: number
  category?: string
  search?: string
}): Promise<ProductListResponse> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.category) q.set('category', params.category)
  if (params.search) q.set('search', params.search)
  const qs = q.toString()
  const path = `/api/catalog/products${qs ? `?${qs}` : ''}`
  return cachedRequest(`catalog:products:${path}`, () => request<ProductListResponse>(path))
}

export function fetchProductBySlug(slug: string): Promise<Product> {
  const path = `/api/catalog/products/${encodeURIComponent(slug)}`
  return cachedRequest(`catalog:product:${path}`, () => request<Product>(path))
}

export function formatPrice(price: string | number): string {
  const n = typeof price === 'string' ? Number(price) : price
  if (Number.isNaN(n)) return String(price)
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(n)
}
