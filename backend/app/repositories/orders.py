"""Database queries for authenticated customer orders."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalog import Product
from app.models.commerce import CartItem, Order, OrderItem, ShoppingCart
from app.schemas.orders import DeliveryAddressIn


def get_active_cart_for_update(db: Session, user_id: UUID) -> ShoppingCart | None:
    """Lock the active cart so repeated checkout submissions cannot both succeed."""
    return (
        db.execute(
            select(ShoppingCart)
            .options(
                selectinload(ShoppingCart.items).joinedload(CartItem.product).joinedload(Product.category)
            )
            .where(
                ShoppingCart.user_id == user_id,
                ShoppingCart.status == "active",
            )
            .with_for_update(of=ShoppingCart)
        )
        .scalars()
        .unique()
        .first()
    )


def create_order(
    db: Session,
    user_id: UUID,
    address: DeliveryAddressIn,
    total_amount: Decimal,
    currency: str,
    payment_method: str,
    status: str,
    placed_at: datetime,
) -> Order:
    order = Order(
        user_id=user_id,
        status=status,
        total_amount=total_amount,
        currency=currency,
        placed_at=placed_at,
        delivery_recipient=address.recipient_name,
        delivery_phone=address.phone,
        delivery_address_line1=address.address_line1,
        delivery_address_line2=address.address_line2,
        delivery_city=address.city,
        delivery_postal_code=address.postal_code,
        payment_method=payment_method,
    )
    db.add(order)
    db.flush()
    return order


def add_order_item(
    db: Session,
    order_id: UUID,
    product_id: UUID,
    product_name_snapshot: str,
    quantity: int,
    unit_price_snapshot: Decimal,
    line_total_snapshot: Decimal,
) -> OrderItem:
    item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        product_name_snapshot=product_name_snapshot,
        quantity=quantity,
        unit_price_snapshot=unit_price_snapshot,
        line_total_snapshot=line_total_snapshot,
    )
    db.add(item)
    db.flush()
    return item


def clear_cart(db: Session, cart: ShoppingCart) -> None:
    """Empty and deactivate the cart after its order has been created."""
    for item in list(cart.items):
        db.delete(item)
    cart.status = "inactive"


def list_user_orders(db: Session, user_id: UUID, limit: int, offset: int) -> list[Order]:
    return list(
        db.execute(
            select(Order)
            .options(selectinload(Order.items).joinedload(OrderItem.product))
            .where(Order.user_id == user_id)
            .order_by(Order.placed_at.desc(), Order.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .unique()
        .all()
    )


def get_user_order(db: Session, user_id: UUID, order_id: UUID) -> Order | None:
    return (
        db.execute(
            select(Order)
            .options(selectinload(Order.items).joinedload(OrderItem.product))
            .where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
        )
        .scalars()
        .unique()
        .first()
    )
