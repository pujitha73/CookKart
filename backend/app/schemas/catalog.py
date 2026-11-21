from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    category_id: UUID
    name: str
    slug: str
    description: str | None = None
    price: Decimal
    unit: str | None = None
    size: str | None = None
    image_url: str | None = None
    is_available: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None
    category: CategoryOut | None = None


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    pages: int
