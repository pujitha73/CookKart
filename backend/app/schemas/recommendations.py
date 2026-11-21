"""Response schemas for pantry-based recipe recommendations."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.schemas.recipe import RecipeOut


class RecommendedIngredientOut(BaseModel):
    id: UUID
    name: str
    quantity: str | None = None
    unit: str | None = None
    display_order: int = 0


class RecipeRecommendationOut(BaseModel):
    recipe: RecipeOut
    match_percentage: float
    available_ingredients: list[RecommendedIngredientOut]
    missing_ingredients: list[RecommendedIngredientOut]
    matched_count: int
    required_count: int
    missing_count: int


class RecommendationListOut(BaseModel):
    items: list[RecipeRecommendationOut]
    total: int
    available_ingredient_count: int
