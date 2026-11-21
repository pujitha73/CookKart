"""Business logic for COD checkout, order placement, and order history."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.orders import (
    add_order_item,
    clear_cart,
    create_order,
    get_active_cart_for_update,
    get_user_order,
    list_user_orders,
)
from app.schemas.orders import DeliveryAddressIn, DeliveryAddressOut, OrderItemOut, OrderOut, OrderSummaryOut
from app.services.cart import MAX_CART_QUANTITY

INITIAL_ORDER_STATUS = "placed"
PAYMENT_METHOD_COD = "cod"
ORDER_CURRENCY = "INR"

ALLOWED_ORDER_STATUSES = ("placed", "confirmed", "cancelled")
STATUS_LABELS = {
    "placed": "Placed",
    "confirmed": "Confirmed",
    "cancelled": "Cancelled",
}


class OrderServiceError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class OrderNotFoundError(OrderServiceError):
    status_code = 404


class OrderConflictError(OrderServiceError):
    status_code = 409


class OrderValidationError(OrderServiceError):
    status_code = 422


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


def _order_number(order: Any) -> str:
    placed = order.placed_at or order.created_at
    date_part = placed.strftime("%Y%m%d")
    token = str(order.id).replace("-", "")[:6].upper()
    return f"CK-{date_part}-{token}"


def _status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.replace("_", " ").title())


def _address_out(order: Any) -> DeliveryAddressOut:
    return DeliveryAddressOut(
        recipient_name=order.delivery_recipient,
        phone=order.delivery_phone,
        address_line1=order.delivery_address_line1,
        address_line2=order.delivery_address_line2,
        city=order.delivery_city,
        postal_code=order.delivery_postal_code,
    )


def _item_out(item: Any) -> OrderItemOut:
    return OrderItemOut(
        id=item.id,
        product_id=item.product_id,
        product_name_snapshot=item.product_name_snapshot,
        quantity=item.quantity,
        unit_price=_money(item.unit_price_snapshot),
        line_total=_money(item.line_total_snapshot),
        image_url=item.product.image_url if item.product else None,
        size=item.product.size if item.product else None,
        unit=item.product.unit if item.product else None,
    )


def _summary_out(order: Any) -> OrderSummaryOut:
    return OrderSummaryOut(
        id=order.id,
        order_number=_order_number(order),
        status=order.status,
        status_label=_status_label(order.status),
        total_amount=_money(order.total_amount),
        currency=order.currency,
        placed_at=order.placed_at,
        item_count=sum(item.quantity for item in order.items),
        payment_method=order.payment_method,
    )


def _order_out(order: Any) -> OrderOut:
    return OrderOut(
        **_summary_out(order).model_dump(),
        delivery_address=_address_out(order),
        items=[_item_out(item) for item in order.items],
    )


def place_order(db: Session, user_id: UUID, address: DeliveryAddressIn) -> OrderOut:
    """Create a COD order from the active cart in one atomic transaction."""
    cart = get_active_cart_for_update(db, user_id)
    if cart is None or not cart.items:
        raise OrderValidationError("Your cart is empty")

    lines: list[dict[str, Any]] = []
    for item in cart.items:
        product = item.product
        if product is None or not product.is_available:
            name = product.name if product else "A product in your cart"
            raise OrderConflictError(f"{name} is no longer available")
        if item.quantity < 1 or item.quantity > MAX_CART_QUANTITY:
            raise OrderValidationError(f"Quantity for {product.name} is invalid")
        if product.price is None or product.price < 0:
            raise OrderValidationError(f"Price for {product.name} is invalid")

        unit_price = _money(product.price)
        lines.append(
            {
                "product_id": product.id,
                "product_name_snapshot": product.name[:200],
                "quantity": item.quantity,
                "unit_price": unit_price,
                "line_total": _money(unit_price * item.quantity),
            }
        )

    total = _money(sum((line["line_total"] for line in lines), Decimal("0.00")))
    placed_at = datetime.now(timezone.utc)

    try:
        order = create_order(
            db,
            user_id,
            address,
            total,
            ORDER_CURRENCY,
            PAYMENT_METHOD_COD,
            INITIAL_ORDER_STATUS,
            placed_at,
        )
        for line in lines:
            add_order_item(
                db,
                order.id,
                line["product_id"],
                line["product_name_snapshot"],
                line["quantity"],
                line["unit_price"],
                line["line_total"],
            )
        clear_cart(db, cart)
        db.commit()
    except Exception:
        db.rollback()
        raise

    stored = get_user_order(db, user_id, order.id)
    if stored is None:
        raise OrderNotFoundError("Order not found")
    return _order_out(stored)


def list_orders(db: Session, user_id: UUID, limit: int, offset: int) -> list[OrderSummaryOut]:
    return [_summary_out(order) for order in list_user_orders(db, user_id, limit, offset)]


def get_order(db: Session, user_id: UUID, order_id: UUID) -> OrderOut:
    order = get_user_order(db, user_id, order_id)
    if order is None:
        raise OrderNotFoundError("Order not found")
    return _order_out(order)
