import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Check, Pencil, Plus, Search, ShoppingBasket, Trash2, X } from 'lucide-react'
import { Button } from '../../components/Button'
import { Card } from '../../components/Card'
import { ExternalImage } from '../../components/ExternalImage'
import {
  addPantryItem,
  ConflictError,
  deletePantryItem,
  fetchIngredientImageMap,
  fetchKitchenIngredients,
  fetchPantry,
  updatePantryItem,
  type IngredientImageMap,
  type KitchenIngredient,
  type PantryEntry,
} from '../../services/kitchenApi'
import { useKitchenError } from './useKitchenError'

type PantryManagerProps = {
  onPantryChange?: () => void
}

type PantryRowProps = {
  entry: PantryEntry
  busy: boolean
  onSave: (entryId: string, values: { quantity: string | null; unit: string | null; is_available: boolean }) => Promise<void>
  onRemove: (entryId: string) => Promise<void>
  onError: (error: unknown, fallback: string) => void
}

function PantryRow({ entry, busy, onSave, onRemove, onError }: PantryRowProps) {
  const [editing, setEditing] = useState(false)
  const [quantity, setQuantity] = useState(entry.quantity ?? '')
  const [unit, setUnit] = useState(entry.unit ?? '')
  const [available, setAvailable] = useState(entry.is_available)

  useEffect(() => {
    setQuantity(entry.quantity ?? '')
    setUnit(entry.unit ?? '')
    setAvailable(entry.is_available)
    setEditing(false)
  }, [entry])

  async function submit(event: FormEvent) {
    event.preventDefault()
    try {
      await onSave(entry.id, {
        quantity: quantity.trim() || null,
        unit: unit.trim() || null,
        is_available: available,
      })
    } catch (error) {
      onError(error, 'Failed to update this pantry item.')
    }
  }

  if (editing) {
    return (
      <li className="rounded-2xl bg-white/70 p-4 ring-1 ring-forest/10">
        <p className="font-semibold text-forest-dark">{entry.ingredient.name}</p>
        <form onSubmit={submit} className="mt-3 grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
          <label className="block text-xs font-semibold text-forest/70">
            Quantity
            <input
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              inputMode="decimal"
              placeholder="e.g. 2"
              className="mt-1 w-full rounded-full border border-forest/15 bg-white px-4 py-2 text-sm text-forest focus:border-lime"
            />
          </label>
          <label className="block text-xs font-semibold text-forest/70">
            Unit
            <input
              value={unit}
              onChange={(e) => setUnit(e.target.value)}
              maxLength={50}
              placeholder="e.g. cups"
              className="mt-1 w-full rounded-full border border-forest/15 bg-white px-4 py-2 text-sm text-forest focus:border-lime"
            />
          </label>
          <label className="flex items-end gap-2 pb-2 text-xs font-semibold text-forest/70">
            <input
              type="checkbox"
              checked={available}
              onChange={(e) => setAvailable(e.target.checked)}
              className="h-4 w-4 accent-forest"
            />
            Available
          </label>
          <div className="flex gap-2 sm:col-span-3">
            <Button type="submit" size="md" disabled={busy} className="px-4 py-2 text-xs">
              <Check size={14} aria-hidden="true" /> Save
            </Button>
            <Button type="button" variant="ghost" size="md" disabled={busy} onClick={() => setEditing(false)} className="px-4 py-2 text-xs">
              <X size={14} aria-hidden="true" /> Cancel
            </Button>
          </div>
        </form>
      </li>
    )
  }

  return (
    <li className="flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-white/70 p-4 ring-1 ring-forest/10">
      <div>
        <p className="font-semibold text-forest-dark">{entry.ingredient.name}</p>
        <p className="mt-1 text-sm text-forest/70">
          {[entry.quantity, entry.unit].filter(Boolean).join(' ') || 'No quantity set'} ·{' '}
          <span className={entry.is_available ? 'text-forest-dark' : 'text-forest/50'}>
            {entry.is_available ? 'Available' : 'Unavailable'}
          </span>
        </p>
      </div>
      <div className="flex gap-2">
        <Button type="button" variant="ghost" size="md" disabled={busy} onClick={() => setEditing(true)} className="px-3 py-2 text-xs">
          <Pencil size={14} aria-hidden="true" /> Edit
        </Button>
        <Button type="button" variant="ghost" size="md" disabled={busy} onClick={() => void onRemove(entry.id)} className="px-3 py-2 text-xs text-forest hover:text-red-700">
          <Trash2 size={14} aria-hidden="true" /> Remove
        </Button>
      </div>
    </li>
  )
}

export function PantryManager({ onPantryChange }: PantryManagerProps) {
  const handleError = useKitchenError()
  const [ingredients, setIngredients] = useState<KitchenIngredient[]>([])
  const [entries, setEntries] = useState<PantryEntry[]>([])
  const [imageByProductName, setImageByProductName] = useState<IngredientImageMap>(() => new Map())
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)
  const [addingId, setAddingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedIngredientId, setSelectedIngredientId] = useState('')
  const [quantity, setQuantity] = useState('')
  const [unit, setUnit] = useState('')
  const [available, setAvailable] = useState(true)

  const pantryIds = useMemo(() => new Set(entries.map((entry) => entry.ingredient.id)), [entries])

  const filteredIngredients = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    if (!term) return ingredients
    return ingredients.filter(
      (item) =>
        item.name.toLowerCase().includes(term) ||
        item.normalized_name?.toLowerCase().includes(term),
    )
  }, [ingredients, searchTerm])

  const selectedIngredient = ingredients.find((item) => item.id === selectedIngredientId) ?? null

  useEffect(() => {
    if (selectedIngredientId && pantryIds.has(selectedIngredientId)) setSelectedIngredientId('')
  }, [pantryIds, selectedIngredientId])

  useEffect(() => {
    let mounted = true
    fetchIngredientImageMap()
      .then((map) => { if (mounted) setImageByProductName(map) })
      .catch(() => { if (mounted) setImageByProductName(new Map()) })
    return () => { mounted = false }
  }, [])

  async function load() {
    const [catalogue, pantry] = await Promise.all([fetchKitchenIngredients(), fetchPantry()])
    setIngredients(catalogue)
    setEntries(pantry)
  }

  useEffect(() => {
    let mounted = true
    setLoading(true)
    setError(null)
    load()
      .then(() => { if (mounted) setSuccess(null) })
      .catch((e: unknown) => { if (mounted) setError(handleError(e, 'Failed to load your pantry.')) })
      .finally(() => { if (mounted) setLoading(false) })
    return () => { mounted = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function refresh() {
    try {
      await load()
      onPantryChange?.()
    } catch (e) {
      setError(handleError(e, 'Failed to refresh your pantry.'))
    }
  }

  function resetAddDetails() {
    setQuantity('')
    setUnit('')
    setAvailable(true)
    setSelectedIngredientId('')
  }

  async function addIngredient(item: KitchenIngredient) {
    setAddingId(item.id)
    setSelectedIngredientId(item.id)
    setError(null)
    setSuccess(null)
    try {
      const created = await addPantryItem({
        ingredient_id: item.id,
        quantity: quantity.trim() || null,
        unit: unit.trim() || null,
        is_available: available,
      })
      await refresh()
      setSuccess(`${created.ingredient.name} added to your pantry.`)
      resetAddDetails()
    } catch (e) {
      if (e instanceof ConflictError) {
        await refresh()
        setSuccess(`${item.name} is already in your pantry.`)
        resetAddDetails()
      } else {
        setError(handleError(e, 'Failed to add this ingredient.'))
      }
    } finally {
      setAddingId(null)
    }
  }

  async function saveEntry(entryId: string, values: { quantity: string | null; unit: string | null; is_available: boolean }) {
    setBusy(true)
    setSuccess(null)
    try {
      await updatePantryItem(entryId, values)
      await refresh()
      setSuccess('Pantry item updated.')
    } finally {
      setBusy(false)
    }
  }

  async function removeEntry(entryId: string) {
    setBusy(true)
    setError(null)
    setSuccess(null)
    try {
      await deletePantryItem(entryId)
      await refresh()
      setSuccess('Pantry item removed.')
    } catch (e) {
      setError(handleError(e, 'Failed to remove this pantry item.'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card className="p-5 md:p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="eyebrow">My Pantry</p>
          <h2 className="mt-2 font-display text-2xl text-forest-dark">Ingredients on hand</h2>
        </div>
        {!loading && !error ? (
          <span className="rounded-full bg-sage-muted/60 px-3 py-1 text-sm font-semibold text-forest">
            {entries.length} item{entries.length === 1 ? '' : 's'}
          </span>
        ) : null}
      </div>

      {loading ? (
        <div className="mt-6 animate-pulse space-y-3">
          <div className="h-12 rounded-2xl bg-sage-muted/50" />
          <div className="h-28 rounded-2xl bg-sage-muted/50" />
        </div>
      ) : error ? (
        <div className="mt-6 rounded-2xl bg-white/70 p-5 text-center ring-1 ring-forest/10">
          <p className="font-semibold text-forest-dark">{error}</p>
          <div className="mt-4 flex justify-center gap-2">
            <Button type="button" variant="secondary" onClick={() => { setError(null); setLoading(true); load().catch((e: unknown) => setError(handleError(e, 'Failed to load your pantry.'))).finally(() => setLoading(false)) }}>
              Retry
            </Button>
          </div>
        </div>
      ) : (
        <>
          <div className="mt-6 rounded-2xl bg-sage-muted/40 p-4 ring-1 ring-forest/10">
            <label className="relative block">
              <span className="sr-only">Search ingredients</span>
              <Search size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-forest/45" aria-hidden="true" />
              <input
                type="search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search ingredients"
                className="w-full rounded-full border border-forest/15 bg-white py-3 pl-10 pr-4 text-forest placeholder:text-forest/40 focus:border-lime"
              />
            </label>
            <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-xs text-forest/65">
              <span>
                {filteredIngredients.length} of {ingredients.length} ingredient{ingredients.length === 1 ? '' : 's'}
                {searchTerm.trim() ? ` matching “${searchTerm.trim()}”` : ''}
              </span>
              {searchTerm ? (
                <button type="button" onClick={() => setSearchTerm('')} className="font-semibold text-forest hover:text-forest-dark hover:underline">
                  Clear search
                </button>
              ) : (
                <span>Scroll sideways to browse</span>
              )}
            </div>
          </div>

          {filteredIngredients.length ? (
            <div
              className="-mx-1 mt-4 flex snap-x snap-mandatory gap-3 overflow-x-auto overscroll-x-contain px-1 pb-4 touch-pan-x"
              role="list"
              aria-label="Ingredients"
            >
              {filteredIngredients.map((item) => {
                const inPantry = pantryIds.has(item.id)
                const selected = selectedIngredientId === item.id
                const imageUrl = imageByProductName.get(item.name.trim().toLowerCase())
                const adding = addingId === item.id
                return (
                  <div
                    key={item.id}
                    role="listitem"
                    className={`w-[150px] shrink-0 snap-start rounded-2xl bg-white/75 p-3 ring-1 transition-all duration-200 sm:w-[170px] ${
                      selected
                        ? 'bg-white ring-2 ring-lime shadow-[var(--shadow-soft)]'
                        : 'ring-forest/10 hover:-translate-y-0.5 hover:ring-forest/25 hover:shadow-[var(--shadow-soft)]'
                    } ${inPantry ? 'opacity-80' : ''}`}
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedIngredientId(item.id)}
                      aria-pressed={selected}
                      className="block w-full text-left"
                      title={`Select ${item.name}`}
                    >
                      {imageUrl ? (
                        <ExternalImage
                          src={imageUrl}
                          alt={item.name}
                          className="h-24 w-full rounded-xl object-cover"
                          sizes="(min-width: 640px) 170px, 150px"
                        />
                      ) : (
                        <div className="flex h-24 w-full items-center justify-center rounded-xl bg-gradient-to-br from-sage-muted via-cream to-cream-deep text-forest/70">
                          <ShoppingBasket size={28} aria-hidden="true" />
                        </div>
                      )}
                      <p className="mt-3 truncate font-semibold text-forest-dark" title={item.name}>{item.name}</p>
                    </button>
                    <div className="mt-2 flex items-center justify-between gap-2">
                      <span className={`text-[11px] font-semibold ${inPantry ? 'text-forest/60' : selected ? 'text-forest-dark' : 'text-forest/45'}`}>
                        {inPantry ? 'In pantry' : selected ? 'Selected' : 'Select'}
                      </span>
                      <Button
                        type="button"
                        variant={inPantry ? 'ghost' : 'primary'}
                        disabled={inPantry || adding || busy || addingId !== null}
                        onClick={() => void addIngredient(item)}
                        className="px-3 py-1.5 text-xs"
                        aria-label={inPantry ? `${item.name} is already in your pantry` : `Add ${item.name} to pantry`}
                      >
                        {adding ? (
                          'Adding…'
                        ) : inPantry ? (
                          <><Check size={13} aria-hidden="true" /> Added</>
                        ) : (
                          <><Plus size={13} aria-hidden="true" /> Add</>
                        )}
                      </Button>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <p className="mt-4 rounded-2xl border border-dashed border-forest/20 p-8 text-center text-forest/70">
              {searchTerm.trim()
                ? `No ingredients match “${searchTerm.trim()}”. Try another search.`
                : 'No ingredients are available yet.'}
            </p>
          )}

          {selectedIngredient ? (
            <div className="mt-4 rounded-2xl bg-white/70 p-4 ring-1 ring-forest/10">
              <p className="text-xs font-semibold uppercase tracking-[0.12em] text-forest/60">
                Optional details for <span className="text-forest-dark">{selectedIngredient.name}</span>
              </p>
              <p className="mt-1 text-xs text-forest/55">These apply when you use any card’s Add button.</p>
              <div className="mt-3 grid gap-3 sm:grid-cols-[1fr_1fr_auto]">
                <label className="block text-xs font-semibold text-forest/70">
                  Quantity
                  <input
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    inputMode="decimal"
                    placeholder="Optional"
                    disabled={addingId !== null || busy}
                    className="mt-1 w-full rounded-full border border-forest/15 bg-white px-4 py-2.5 text-sm text-forest placeholder:text-forest/40 focus:border-lime"
                  />
                </label>
                <label className="block text-xs font-semibold text-forest/70">
                  Unit
                  <input
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    maxLength={50}
                    placeholder="Optional"
                    disabled={addingId !== null || busy}
                    className="mt-1 w-full rounded-full border border-forest/15 bg-white px-4 py-2.5 text-sm text-forest placeholder:text-forest/40 focus:border-lime"
                  />
                </label>
                <label className="flex items-end gap-2 pb-2 text-xs font-semibold text-forest/70">
                  <input
                    type="checkbox"
                    checked={available}
                    onChange={(e) => setAvailable(e.target.checked)}
                    disabled={addingId !== null || busy}
                    className="h-4 w-4 accent-forest"
                  />
                  Available
                </label>
              </div>
            </div>
          ) : (
            <p className="mt-4 text-xs text-forest/60">
              Select a card to set optional quantity, unit, and availability before adding.
            </p>
          )}

          {success ? <p role="status" className="mt-4 text-sm font-semibold text-forest-dark">{success}</p> : null}

          {entries.length ? (
            <ul className="mt-5 space-y-3">
              {entries.map((entry) => (
                <PantryRow
                  key={entry.id}
                  entry={entry}
                  busy={busy}
                  onSave={saveEntry}
                  onRemove={removeEntry}
                  onError={(e, fallback) => setError(handleError(e, fallback))}
                />
              ))}
            </ul>
          ) : (
            <div className="mt-6 rounded-2xl border border-dashed border-forest/20 p-8 text-center">
              <p className="font-semibold text-forest-dark">Your pantry is empty</p>
              <p className="mt-2 text-sm text-forest/70">Add an ingredient from the cards above to get started.</p>
            </div>
          )}
        </>
      )}
    </Card>
  )
}
