"""Pydantic response schemas for the recipe catalogue."""

from __future__ import annotations

import json
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.recipe import RecipeIngredient


class RecipeCollectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    cuisine_label: str | None = None
    description: str | None = None
    recipe_count: int = 0


class RecipeIngredientOut(BaseModel):
    name: str
    quantity: str | None = None
    unit: str | None = None
    preparation_note: str | None = None
    display_order: int = 0


class RecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None = None
    meal_type: str
    prep_time_minutes: int | None = None
    cook_time_minutes: int | None = None
    difficulty: str | None = None
    serving_size: int | None = None
    image_url: str | None = None
    youtube_video_id: str | None = None
    youtube_url: str | None = None
    collection: RecipeCollectionOut | None = None


class RecipeDetailOut(RecipeOut):
    instructions: list[str] = []
    ingredients: list[RecipeIngredientOut] = []


class RecipeListOut(BaseModel):
    items: list[RecipeOut]
    total: int
    page: int
    page_size: int
    pages: int


def parse_instructions(raw: str | None) -> list[str]:
    """Read ordered steps stored as a JSON array, falling back to newline text."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [str(step).strip() for step in parsed if str(step).strip()]
    except (TypeError, ValueError):
        pass
    return [line.strip() for line in raw.splitlines() if line.strip()]


def ingredient_out(link: RecipeIngredient) -> RecipeIngredientOut:
    """Serialize a recipe-ingredient link using its canonical ingredient name."""
    quantity: str | None = None
    if link.quantity is not None:
        value = link.quantity
        quantity = format(value.normalize(), "f") if isinstance(value, Decimal) else str(value)
    return RecipeIngredientOut(
        name=link.ingredient.name,
        quantity=quantity,
        unit=link.unit,
        preparation_note=link.preparation_note,
        display_order=link.display_order,
    )
