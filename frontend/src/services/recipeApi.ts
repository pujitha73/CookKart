import { cachedRequest } from './requestCache'

export type RecipeCollection = {
  id: string
  name: string
  slug: string
  cuisine_label?: string | null
  description?: string | null
  recipe_count: number
}

export type Recipe = {
  id: string
  name: string
  slug: string
  description?: string | null
  meal_type: string
  prep_time_minutes?: number | null
  cook_time_minutes?: number | null
  difficulty?: string | null
  serving_size?: number | null
  image_url?: string | null
  youtube_video_id?: string | null
  youtube_url?: string | null
  collection?: RecipeCollection | null
}

export type RecipeIngredient = {
  name: string
  quantity?: string | null
  unit?: string | null
  preparation_note?: string | null
  display_order: number
}

export type RecipeDetail = Recipe & {
  instructions: string[]
  ingredients: RecipeIngredient[]
}

export type RecipeListResponse = {
  items: Recipe[]
  total: number
  page: number
  page_size: number
  pages: number
}

export const MEAL_TYPE_FILTERS = [
  { value: '', label: 'All meal types' },
  { value: 'breakfast-tiffin', label: 'Breakfast / Tiffin' },
  { value: 'lunch-dinner', label: 'Lunch / Dinner' },
  { value: 'snack', label: 'Snack' },
] as const

export function mealTypeLabel(value: string): string {
  return MEAL_TYPE_FILTERS.find((item) => item.value === value)?.label || value
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
      if (data?.detail) {
        message = typeof data.detail === 'string' ? data.detail : 'Invalid recipe search parameters'
      }
    } catch {
      // ignore
    }
    throw new Error(message)
  }
  return res.json() as Promise<T>
}

export function fetchRecipeCollections(): Promise<RecipeCollection[]> {
  return cachedRequest('recipes:collections', () => request<RecipeCollection[]>('/api/recipes/collections'))
}

export function fetchRecipes(params: {
  page?: number
  page_size?: number
  collection?: string
  meal_type?: string
  search?: string
}): Promise<RecipeListResponse> {
  const q = new URLSearchParams()
  if (params.page) q.set('page', String(params.page))
  if (params.page_size) q.set('page_size', String(params.page_size))
  if (params.collection) q.set('collection', params.collection)
  if (params.meal_type) q.set('meal_type', params.meal_type)
  if (params.search) q.set('search', params.search)
  const qs = q.toString()
  const path = `/api/recipes${qs ? `?${qs}` : ''}`
  return cachedRequest(`recipes:list:${path}`, () => request<RecipeListResponse>(path))
}

export function fetchRecipeBySlug(slug: string): Promise<RecipeDetail> {
  const path = `/api/recipes/${encodeURIComponent(slug)}`
  return cachedRequest(`recipes:detail:${path}`, () => request<RecipeDetail>(path))
}

export function formatRecipeTime(minutes?: number | null): string {
  if (!minutes) return '—'
  return `${minutes} min`
}

export function formatIngredientAmount(quantity?: string | null, unit?: string | null): string {
  const q = quantity?.trim() ?? ''
  const u = unit?.trim() ?? ''
  if (!q) return u
  if (!u) return q
  return `${q} ${u}`
}
