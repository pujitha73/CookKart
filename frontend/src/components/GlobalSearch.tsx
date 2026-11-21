import { useEffect, useId, useRef, useState, type KeyboardEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search } from 'lucide-react'
import { fetchProducts, type Product } from '../services/catalogApi'
import { fetchRecipes, type Recipe } from '../services/recipeApi'

type SearchResult = {
  kind: 'product' | 'recipe'
  id: string
  name: string
  subtitle: string
  slug: string
}

type Props = {
  variant?: 'desktop' | 'mobile'
  onNavigate?: () => void
}

const DESKTOP_INPUT_CLASS =
  'w-64 rounded-full border border-forest/10 bg-white/80 py-2.5 pl-9 pr-4 text-sm text-forest placeholder:text-forest/45 focus:border-lime focus:bg-white focus:outline-none'
const MOBILE_INPUT_CLASS =
  'w-full rounded-full border border-forest/10 bg-white/80 py-2.5 pl-9 pr-4 text-sm text-forest placeholder:text-forest/45 focus:border-lime focus:bg-white focus:outline-none'

function toProductResult(product: Product): SearchResult {
  return {
    kind: 'product',
    id: product.id,
    name: product.name,
    subtitle: product.category?.name ?? 'Grocery',
    slug: product.slug,
  }
}

function toRecipeResult(recipe: Recipe): SearchResult {
  return {
    kind: 'recipe',
    id: recipe.id,
    name: recipe.name,
    subtitle: 'Recipe',
    slug: recipe.slug,
  }
}

/**
 * Header search across the public product and recipe catalogues. Uses only
 * unauthenticated endpoints so it behaves identically for guests and signed-in
 * customers.
 */
export function GlobalSearch({ variant = 'desktop', onNavigate }: Props) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [active, setActive] = useState(-1)
  const navigate = useNavigate()
  const wrapperRef = useRef<HTMLDivElement>(null)
  const listId = useId()

  useEffect(() => {
    const term = query.trim()
    if (term.length < 2) {
      setResults([])
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    const timer = window.setTimeout(() => {
      Promise.all([
        fetchProducts({ search: term, page_size: 5 }),
        fetchRecipes({ search: term, page_size: 5 }),
      ])
        .then(([products, recipes]) => {
          if (cancelled) return
          setResults([
            ...products.items.map(toProductResult),
            ...recipes.items.map(toRecipeResult),
          ])
          setActive(-1)
        })
        .catch(() => {
          if (!cancelled) setResults([])
        })
        .finally(() => {
          if (!cancelled) setLoading(false)
        })
    }, 180)

    return () => {
      cancelled = true
      window.clearTimeout(timer)
    }
  }, [query])

  useEffect(() => {
    if (!open) return
    function onPointerDown(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onPointerDown)
    return () => document.removeEventListener('mousedown', onPointerDown)
  }, [open])

  function close() {
    setOpen(false)
    setActive(-1)
  }

  function goToResult(result: SearchResult) {
    close()
    setQuery('')
    onNavigate?.()
    navigate(result.kind === 'product' ? `/shop/${result.slug}` : `/recipes/${result.slug}`)
  }

  function submitSearch() {
    const term = query.trim()
    if (!term) return
    if (results.length) {
      goToResult(results[active >= 0 ? active : 0])
      return
    }
    // No direct match: fall back to the existing Shop page product search.
    close()
    onNavigate?.()
    navigate(`/shop?search=${encodeURIComponent(term)}`)
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setOpen(true)
      setActive((current) => (results.length ? Math.min(current + 1, results.length - 1) : -1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActive((current) => Math.max(current - 1, -1))
    } else if (event.key === 'Enter') {
      event.preventDefault()
      submitSearch()
    } else if (event.key === 'Escape') {
      event.preventDefault()
      close()
    }
  }

  const showDropdown = open && query.trim().length >= 2
  let lastKind: SearchResult['kind'] | null = null

  return (
    <div ref={wrapperRef} className="relative block">
      <label className="relative block">
        <span className="sr-only">Search products and recipes</span>
        <Search
          size={16}
          className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-forest/50"
          aria-hidden="true"
        />
        <input
          type="search"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value)
            setOpen(true)
            setActive(-1)
          }}
          onFocus={() => setOpen(true)}
          onClick={() => setOpen(true)}
          onKeyDown={onKeyDown}
          placeholder="Search groceries & recipes"
          className={variant === 'desktop' ? DESKTOP_INPUT_CLASS : MOBILE_INPUT_CLASS}
          role="combobox"
          aria-label="Search products and recipes"
          aria-expanded={showDropdown}
          aria-controls={listId}
          aria-autocomplete="list"
          aria-activedescendant={active >= 0 ? `${listId}-option-${active}` : undefined}
          autoComplete="off"
        />
      </label>

      {showDropdown ? (
        <div className={`absolute left-0 top-full z-[60] mt-2 overflow-hidden rounded-2xl border border-forest/10 bg-white shadow-[var(--shadow-lift)] ${variant === 'desktop' ? 'w-80' : 'w-full'}`}>
          {loading && results.length === 0 ? (
            <p className="px-4 py-3 text-sm text-forest/65">Searching…</p>
          ) : results.length === 0 ? (
            <p className="px-4 py-3 text-sm text-forest/65">
              No matches. Press Enter to search the shop.
            </p>
          ) : (
            <ul id={listId} role="listbox" aria-label="Search results" className="max-h-80 overflow-y-auto py-1">
              {results.map((result, index) => {
                const showHeading = result.kind !== lastKind
                lastKind = result.kind
                return (
                  <li key={`${result.kind}-${result.id}`} role="presentation">
                    {showHeading ? (
                      <p className="px-4 pb-1 pt-2 text-[11px] font-bold uppercase tracking-[0.14em] text-forest/50">
                        {result.kind === 'product' ? 'Products' : 'Recipes'}
                      </p>
                    ) : null}
                    <button
                      type="button"
                      id={`${listId}-option-${index}`}
                      role="option"
                      aria-selected={active === index}
                      onMouseEnter={() => setActive(index)}
                      onClick={() => goToResult(result)}
                      className={`flex w-full flex-col items-start px-4 py-2 text-left transition-colors ${
                        active === index ? 'bg-sage-muted/70' : 'hover:bg-sage-muted/50'
                      }`}
                    >
                      <span className="text-sm font-semibold text-forest-dark">{result.name}</span>
                      <span className="text-xs text-forest/60">{result.subtitle}</span>
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </div>
      ) : null}
    </div>
  )
}
