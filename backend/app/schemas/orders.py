"""Request and response schemas for COD checkout and order history."""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PHONE_PATTERN = re.compile(r"^[0-9+()\-\s]{10,20}$")
POSTAL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 -]{2,19}$")


class DeliveryAddressIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recipient_name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=10, max_length=20)
    address_line1: str = Field(min_length=5, max_length=200)
    address_line2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=3, max_length=20)

    @field_validator("recipient_name", "address_line1", "city")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field is required")
        return value

    @field_validator("address_line2")
    @classmethod
    def _strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("phone")
    @classmethod
    def _validate_phone(cls, value: str) -> str:
        value = value.strip()
        if not PHONE_PATTERN.fullmatch(value):
            raise ValueError("Enter a valid phone number")
        return value

    @field_validator("postal_code")
    @classmethod
    def _validate_postal_code(cls, value: str) -> str:
        value = value.strip()
        if not POSTAL_PATTERN.fullmatch(value):
            raise ValueError("Enter a valid postal code")
        return value


class OrderCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delivery_address: DeliveryAddressIn


class DeliveryAddressOut(BaseModel):
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None = None
    city: str
    postal_code: str

    def display_text(self) -> str:
        lines = [self.address_line1]
        if self.address_line2:
            lines.append(self.address_line2)
        lines.append(f"{self.city} {self.postal_code}")
        return "\n".join(lines)


class OrderItemOut(BaseModel):
    id: UUID
    product_id: UUID | None = None
    product_name_snapshot: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    image_url: str | None = None
    size: str | None = None
    unit: str | None = None


class OrderSummaryOut(BaseModel):
    id: UUID
    order_number: str
    status: str
    status_label: str
    total_amount: Decimal
    currency: str
    placed_at: datetime
    item_count: int
    payment_method: str


class OrderOut(OrderSummaryOut):
    delivery_address: DeliveryAddressOut
    items: list[OrderItemOut]
