"""Safe helpers for user-supplied substring search filters."""

from __future__ import annotations


def ilike_contains(column, term: str | None):
    """Case-insensitive substring match that treats LIKE wildcards literally.

    User input is always bound as a parameter, and ``%``, ``_`` and ``\\`` are
    escaped so a search for ``%`` does not unintentionally match every row.
    """
    if not term or not term.strip():
        return None
    escaped = (
        term.strip()
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return column.ilike(f"%{escaped}%", escape="\\")
