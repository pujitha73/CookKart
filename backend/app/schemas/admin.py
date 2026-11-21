"""Request and response schemas for administrator APIs."""

from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.orders import OrderSummaryOut

ADMIN_ORDER_STATUSES = ("placed", "confirmed", "cancelled")
ADMIN_PRODUCT_AVAILABILITY = ("all", "available", "unavailable")


class AdminMeOut(BaseModel):
    user_id: UUID
    email: str | None = None
    is_admin: bool = True


class AdminCatalogueOut(BaseModel):
    total_products: int
    available_products: int
    unavailable_products: int
    total_categories: int


class AdminDashboardOut(BaseModel):
    total_orders: int
    awaiting_confirmation: int
    confirmed_orders: int
    cancelled_orders: int
    catalogue: AdminCatalogueOut


class AdminOrderListOut(BaseModel):
    items: list[OrderSummaryOut]
    total: int
    page: int
    page_size: int
    pages: int


class OrderStatusUpdateIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["placed", "confirmed", "cancelled"]


class ProductAvailabilityIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_available: bool
