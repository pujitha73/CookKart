function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * Formats a product's quantity from its `size` and `unit` fields.
 *
 * `size` may already contain the unit (for example "1 kg", "500 ml", or
 * "12 pcs"), in which case the unit is not appended again. When `size` only
 * contains a number (for example "5" with unit "kg"), the unit is appended.
 */
export function formatQuantity(size?: string | null, unit?: string | null): string {
  const sizeValue = size?.trim() ?? ''
  const unitValue = unit?.trim() ?? ''

  if (!sizeValue) return unitValue
  if (!unitValue) return sizeValue

  // Matches the unit at the end of the size, allowing a plural suffix.
  const unitAtEnd = new RegExp(`(^|[^a-z])${escapeRegExp(unitValue.toLowerCase())}s?$`, 'i')
  if (unitAtEnd.test(sizeValue)) return sizeValue

  // A size ending in a word already describes its own unit (e.g. "12 pcs").
  if (/[a-z]$/i.test(sizeValue)) return sizeValue

  return `${sizeValue} ${unitValue}`
}
