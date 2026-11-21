"""Administrator-only dashboard, order management, and availability APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.admin import CurrentAdmin
from app.database.session import get_db
from app.schemas.admin import (
    ADMIN_ORDER_STATUSES,
    ADMIN_PRODUCT_AVAILABILITY,
    AdminDashboardOut,
    AdminMeOut,
    AdminOrderListOut,
    OrderStatusUpdateIn,
    ProductAvailabilityIn,
)
from app.schemas.catalog import ProductListOut, ProductOut
from app.schemas.orders import OrderOut
from app.services import admin as admin_service
from app.services.admin import AdminServiceError

router = APIRouter(prefix="/admin", tags=["admin"])


def _service_error(exc: AdminServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.get("/me", response_model=AdminMeOut)
def admin_me(current_admin: CurrentAdmin):
    """Called by the frontend to decide whether to expose admin UI."""
    return AdminMeOut(user_id=current_admin.id, email=current_admin.email)


@router.get("/dashboard", response_model=AdminDashboardOut)
def get_dashboard(
    current_admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    return admin_service.get_dashboard(db)


@router.get("/orders", response_model=AdminOrderListOut)
def list_orders(
    current_admin: CurrentAdmin,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Search by order number"),
    status_filter: str | None = Query(
        None, alias="status", description="placed | confirmed | cancelled"
    ),
):
    if status_filter is not None and status_filter not in ADMIN_ORDER_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid order status filter")
    return admin_service.list_admin_orders(db, search, status_filter, page, page_size)


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order(
    order_id: UUID,
    current_admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    try:
        return admin_service.get_admin_order(db, order_id)
    except AdminServiceError as exc:
        raise _service_error(exc) from exc


@router.patch("/orders/{order_id}/status", response_model=OrderOut)
def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdateIn,
    current_admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    try:
        return admin_service.update_order_status(db, order_id, payload.status)
    except AdminServiceError as exc:
        raise _service_error(exc) from exc


@router.get("/products", response_model=ProductListOut)
def list_products(
    current_admin: CurrentAdmin,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, description="Search by product name"),
    availability: str | None = Query(
        None, description="all | available | unavailable"
    ),
):
    if availability is not None and availability not in ADMIN_PRODUCT_AVAILABILITY:
        raise HTTPException(status_code=422, detail="Invalid availability filter")
    normalized = None if availability in (None, "all") else availability
    return admin_service.list_admin_products(db, search, normalized, page, page_size)


@router.patch("/products/{product_id}/availability", response_model=ProductOut)
def set_product_availability(
    product_id: UUID,
    payload: ProductAvailabilityIn,
    current_admin: CurrentAdmin,
    db: Session = Depends(get_db),
):
    try:
        return admin_service.set_product_availability(db, product_id, payload.is_available)
    except AdminServiceError as exc:
        raise _service_error(exc) from exc
