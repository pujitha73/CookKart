"""Authenticated COD checkout and customer order history APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import CurrentUser
from app.database.session import get_db
from app.schemas.orders import OrderCreateRequest, OrderOut, OrderSummaryOut
from app.services.orders import (
    OrderServiceError,
    get_order,
    list_orders,
    place_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def _service_error(exc: OrderServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    response: Response,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        order = place_order(db, current_user.id, payload.delivery_address)
    except OrderServiceError as exc:
        raise _service_error(exc) from exc
    response.status_code = status.HTTP_201_CREATED
    return order


@router.get("", response_model=list[OrderSummaryOut])
def get_orders(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    try:
        return list_orders(db, current_user.id, limit, offset)
    except OrderServiceError as exc:
        raise _service_error(exc) from exc


@router.get("/{order_id}", response_model=OrderOut)
def get_order_detail(
    order_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        return get_order(db, current_user.id, order_id)
    except OrderServiceError as exc:
        raise _service_error(exc) from exc
