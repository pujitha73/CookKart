"""Request and response schemas for My Kitchen."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.recipe import RecipeOut


def decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value.normalize(), "f")


class IngredientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    normalized_name: str | None = None


class PantryEntryBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=50)
    is_available: bool = True


class PantryEntryCreate(PantryEntryBase):
    ingredient_id: UUID


class PantryEntryUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=50)
    is_available: bool | None = None


class PantryEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ingredient: IngredientOut
    quantity: str | None = None
    unit: str | None = None
    is_available: bool
    created_at: datetime
    updated_at: datetime


class SavedRecipeCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipe_id: UUID


class SavedRecipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    recipe: RecipeOut
    saved_at: datetime
