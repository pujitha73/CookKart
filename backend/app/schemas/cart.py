"""Request and response schemas for the shopping cart and recipe-to-cart flows."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.catalog import ProductOut
from app.schemas.recipe import RecipeOut


class CartItemCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: UUID
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantity: int = Field(ge=1, le=99)


class CartItemOut(BaseModel):
    id: UUID
    product: ProductOut
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CartOut(BaseModel):
    items: list[CartItemOut]
    item_count: int
    line_count: int
    total: Decimal
    unavailable_item_count: int


class RecipeCartAddRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_ids: list[UUID] = Field(min_length=1, max_length=50)


class MissingProductOut(BaseModel):
    id: UUID
    name: str
    slug: str
    price: Decimal
    unit: str | None = None
    size: str | None = None
    image_url: str | None = None
    match_priority: int
    substitution_note: str | None = None
    cart_quantity: int = 1


class MissingIngredientOut(BaseModel):
    id: UUID
    name: str
    quantity: str | None = None
    unit: str | None = None
    preparation_note: str | None = None
    display_order: int
    status: Literal["available", "unmapped", "unavailable"]
    products: list[MissingProductOut]


class RecipeCartPlanOut(BaseModel):
    recipe: RecipeOut
    missing_ingredients: list[MissingIngredientOut]
    required_count: int
    available_pantry_count: int
    missing_count: int
    matched_missing_count: int
    unmapped_missing_count: int
    unavailable_missing_count: int
    default_cart_quantity: int = 1
    quantity_note: str


class RecipeCartAddOut(BaseModel):
    cart: CartOut
    products_added: int
    added_product_ids: list[UUID]
