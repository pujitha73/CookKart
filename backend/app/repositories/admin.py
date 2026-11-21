"""Database queries for administrator order and catalogue management."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalog import Product, ProductCategory
from app.models.commerce import Order, OrderItem
from app.utils.search import ilike_contains


def list_all_orders(db: Session, status: str | None = None) -> list[Order]:
    """Return every order (optionally filtered by status), newest first."""
    stmt = select(Order).options(selectinload(Order.items).joinedload(OrderItem.product))
    if status is not None:
        stmt = stmt.where(Order.status == status)
    stmt = stmt.order_by(Order.placed_at.desc(), Order.created_at.desc())
    return list(db.execute(stmt).scalars().unique().all())


def get_order_by_id(db: Session, order_id: UUID, for_update: bool = False) -> Order | None:
    stmt = (
        select(Order)
        .options(selectinload(Order.items).joinedload(OrderItem.product))
        .where(Order.id == order_id)
    )
    if for_update:
        stmt = stmt.with_for_update(of=Order)
    return db.execute(stmt).scalars().unique().first()


def count_orders_by_status(db: Session) -> dict[str, int]:
    rows = db.execute(select(Order.status, func.count()).group_by(Order.status)).all()
    return {str(status): int(count) for status, count in rows}


def catalogue_counts(db: Session) -> tuple[int, int, int, int]:
    """Return (total products, available, unavailable, total categories)."""
    total_products, available_products = db.execute(
        select(
            func.count(),
            func.count().filter(Product.is_available.is_(True)),
        )
    ).one()
    total_categories = db.execute(
        select(func.count()).select_from(ProductCategory)
    ).scalar_one()
    total = int(total_products)
    available = int(available_products)
    return total, available, total - available, int(total_categories)


def list_all_products(
    db: Session,
    search: str | None,
    availability: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Product], int]:
    """List all catalogue products, including unavailable ones."""
    filters = []
    if search:
        name_filter = ilike_contains(Product.name, search)
        if name_filter is not None:
            filters.append(name_filter)
    if availability == "available":
        filters.append(Product.is_available.is_(True))
    elif availability == "unavailable":
        filters.append(Product.is_available.is_(False))

    base = select(Product).options(joinedload(Product.category)).where(*filters)
    total = db.execute(
        select(func.count()).select_from(select(Product.id).where(*filters).subquery())
    ).scalar_one()
    items = (
        db.execute(
            base.order_by(Product.name.asc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        .scalars()
        .unique()
        .all()
    )
    return list(items), int(total)


def get_product_by_id(db: Session, product_id: UUID, for_update: bool = False) -> Product | None:
    stmt = (
        select(Product)
        .options(joinedload(Product.category))
        .where(Product.id == product_id)
    )
    if for_update:
        stmt = stmt.with_for_update(of=Product)
    return db.execute(stmt).scalars().unique().first()
