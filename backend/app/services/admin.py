"""Business logic for the administrator dashboard, orders, and catalogue."""

from __future__ import annotations

from math import ceil
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories import admin as admin_repo
from app.schemas.admin import AdminCatalogueOut, AdminDashboardOut, AdminOrderListOut
from app.schemas.catalog import ProductListOut, ProductOut
from app.schemas.orders import OrderOut
from app.services.orders import _order_out, _summary_out

# Explicit, one-way status transitions. Reopening or editing finished orders is
# intentionally not supported.
ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "placed": {"confirmed", "cancelled"},
    "confirmed": {"cancelled"},
    "cancelled": set(),
}


class AdminServiceError(Exception):
    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class AdminNotFoundError(AdminServiceError):
    status_code = 404


class AdminTransitionError(AdminServiceError):
    status_code = 409


def get_dashboard(db: Session) -> AdminDashboardOut:
    """Build dashboard counters from real database records only."""
    statuses = admin_repo.count_orders_by_status(db)
    total_products, available, unavailable, total_categories = admin_repo.catalogue_counts(db)
    return AdminDashboardOut(
        total_orders=sum(statuses.values()),
        awaiting_confirmation=statuses.get("placed", 0),
        confirmed_orders=statuses.get("confirmed", 0),
        cancelled_orders=statuses.get("cancelled", 0),
        catalogue=AdminCatalogueOut(
            total_products=total_products,
            available_products=available,
            unavailable_products=unavailable,
            total_categories=total_categories,
        ),
    )


def list_admin_orders(
    db: Session,
    search: str | None,
    status: str | None,
    page: int,
    page_size: int,
) -> AdminOrderListOut:
    summaries = [_summary_out(order) for order in admin_repo.list_all_orders(db, status)]
    if search:
        term = search.strip().lower()
        summaries = [item for item in summaries if term in item.order_number.lower()]

    total = len(summaries)
    start = (page - 1) * page_size
    return AdminOrderListOut(
        items=summaries[start : start + page_size],
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total else 0,
    )


def get_admin_order(db: Session, order_id: UUID) -> OrderOut:
    order = admin_repo.get_order_by_id(db, order_id)
    if order is None:
        raise AdminNotFoundError("Order not found")
    return _order_out(order)


def update_order_status(db: Session, order_id: UUID, new_status: str) -> OrderOut:
    """Change only the status column, preserving snapshots and totals."""
    try:
        order = admin_repo.get_order_by_id(db, order_id, for_update=True)
        if order is None:
            raise AdminNotFoundError("Order not found")

        current_status = order.status
        if new_status not in ALLOWED_TRANSITIONS.get(current_status, set()):
            raise AdminTransitionError(
                f"Cannot change order status from '{current_status}' to '{new_status}'"
            )

        order.status = new_status
        db.commit()
    except Exception:
        db.rollback()
        raise

    stored = admin_repo.get_order_by_id(db, order_id)
    if stored is None:
        raise AdminNotFoundError("Order not found")
    return _order_out(stored)


def list_admin_products(
    db: Session,
    search: str | None,
    availability: str | None,
    page: int,
    page_size: int,
) -> ProductListOut:
    items, total = admin_repo.list_all_products(db, search, availability, page, page_size)
    return ProductListOut(
        items=[ProductOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=ceil(total / page_size) if total else 0,
    )


def set_product_availability(
    db: Session,
    product_id: UUID,
    is_available: bool,
) -> ProductOut:
    """Toggle only is_available; never touch product price or catalogue data."""
    try:
        product = admin_repo.get_product_by_id(db, product_id, for_update=True)
        if product is None:
            raise AdminNotFoundError("Product not found")

        product.is_available = is_available
        db.commit()
    except Exception:
        db.rollback()
        raise

    stored = admin_repo.get_product_by_id(db, product_id)
    if stored is None:
        raise AdminNotFoundError("Product not found")
    return ProductOut.model_validate(stored)
