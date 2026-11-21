import { INGREDIENT_IMAGE_URLS } from './ingredientImages'
import type { Recipe } from './recipeApi'
import { supabase } from './supabaseClient'

export type KitchenIngredient = {
  id: string
  name: string
  normalized_name?: string | null
}

export type PantryEntry = {
  id: string
  ingredient: KitchenIngredient
  quantity?: string | null
  unit?: string | null
  is_available: boolean
  created_at: string
  updated_at: string
}

export type SavedRecipe = {
  id: string
  recipe: Recipe
  saved_at: string
}

export type RecommendedIngredient = {
  id: string
  name: string
  quantity?: string | null
  unit?: string | null
  display_order: number
}

export type RecipeRecommendation = {
  recipe: Recipe
  match_percentage: number
  available_ingredients: RecommendedIngredient[]
  missing_ingredients: RecommendedIngredient[]
  matched_count: number
  required_count: number
  missing_count: number
}

export type RecommendationListResponse = {
  items: RecipeRecommendation[]
  total: number
  available_ingredient_count: number
}

export type PantryCreatePayload = {
  ingredient_id: string
  quantity?: string | null
  unit?: string | null
  is_available?: boolean
}

export type PantryUpdatePayload = {
  quantity?: string | null
  unit?: string | null
  is_available?: boolean
}

export class AuthenticationError extends Error {
  constructor(message = 'Your session has expired. Please sign in again.') {
    super(message)
    this.name = 'AuthenticationError'
  }
}

export class ConflictError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'ConflictError'
  }
}

const API_BASE = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '') || ''

function errorMessage(payload: unknown, fallback: string): string {
  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detail = (payload as { detail?: unknown }).detail
    if (typeof detail === 'string' && detail.trim()) return detail
  }
  return fallback
}

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
    const message = errorMessage(payload, `Request failed (${res.status})`)
    if (res.status === 409) throw new ConflictError(message)
    throw new Error(message)
  }

  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export type IngredientImageMap = Map<string, string>

/**
 * Returns the curated ingredient image catalogue keyed by normalized name.
 *
 * Previously this was derived from exact catalogue product-name matches, which
 * left most ingredients without an image. The static map covers every pantry
 * ingredient explicitly, so it is independent of the product catalogue and
 * cannot silently produce missing or duplicate images.
 */
export async function fetchIngredientImageMap(): Promise<IngredientImageMap> {
  return new Map(Object.entries(INGREDIENT_IMAGE_URLS))
}

export function fetchKitchenIngredients(): Promise<KitchenIngredient[]> {
  return request<KitchenIngredient[]>('/api/kitchen/ingredients')
}

export function fetchPantry(): Promise<PantryEntry[]> {
  return request<PantryEntry[]>('/api/kitchen/pantry')
}

export function fetchRecommendations(params: {
  meal_type?: string
  collection?: string
} = {}): Promise<RecommendationListResponse> {
  const query = new URLSearchParams()
  if (params.meal_type) query.set('meal_type', params.meal_type)
  if (params.collection) query.set('collection', params.collection)
  const qs = query.toString()
  return request<RecommendationListResponse>(
    `/api/kitchen/recommendations${qs ? `?${qs}` : ''}`,
  )
}

export function addPantryItem(payload: PantryCreatePayload): Promise<PantryEntry> {
  return request<PantryEntry>('/api/kitchen/pantry', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updatePantryItem(entryId: string, payload: PantryUpdatePayload): Promise<PantryEntry> {
  return request<PantryEntry>(`/api/kitchen/pantry/${encodeURIComponent(entryId)}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function deletePantryItem(entryId: string): Promise<void> {
  return request<void>(`/api/kitchen/pantry/${encodeURIComponent(entryId)}`, {
    method: 'DELETE',
  })
}

export function fetchSavedRecipes(): Promise<SavedRecipe[]> {
  return request<SavedRecipe[]>('/api/kitchen/saved-recipes')
}

export function saveRecipe(recipeId: string): Promise<SavedRecipe> {
  return request<SavedRecipe>('/api/kitchen/saved-recipes', {
    method: 'POST',
    body: JSON.stringify({ recipe_id: recipeId }),
  })
}

export function unsaveRecipe(recipeId: string): Promise<void> {
  return request<void>(`/api/kitchen/saved-recipes/${encodeURIComponent(recipeId)}`, {
    method: 'DELETE',
  })
}
