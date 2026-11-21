"""Authenticated shopping cart and Smart Recipe-to-Cart APIs."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.auth import CurrentUser
from app.database.session import get_db
from app.schemas.cart import (
    CartItemCreate,
    CartItemOut,
    CartItemUpdate,
    CartOut,
    RecipeCartAddOut,
    RecipeCartAddRequest,
    RecipeCartPlanOut,
)
from app.services.cart import (
    CartServiceError,
    add_item,
    add_selected_recipe_products,
    build_recipe_cart_plan,
    get_cart,
    remove_item,
    update_item,
)

router = APIRouter(prefix="/cart", tags=["cart"])


def _service_error(exc: CartServiceError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


@router.get("", response_model=CartOut)
def get_current_cart(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    return get_cart(db, current_user.id)


@router.post("/items", response_model=CartItemOut)
def add_cart_item(
    payload: CartItemCreate,
    response: Response,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        item, created = add_item(
            db,
            current_user.id,
            payload.product_id,
            payload.quantity,
        )
    except CartServiceError as exc:
        raise _service_error(exc) from exc
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return item


@router.patch("/items/{item_id}", response_model=CartItemOut)
def update_cart_item(
    item_id: UUID,
    payload: CartItemUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        return update_item(db, current_user.id, item_id, payload.quantity)
    except CartServiceError as exc:
        raise _service_error(exc) from exc


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_cart_item(
    item_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        remove_item(db, current_user.id, item_id)
    except CartServiceError as exc:
        raise _service_error(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/recipes/{recipe_slug}/plan", response_model=RecipeCartPlanOut)
def get_recipe_cart_plan(
    recipe_slug: str,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        return build_recipe_cart_plan(db, current_user.id, recipe_slug)
    except CartServiceError as exc:
        raise _service_error(exc) from exc


@router.post("/recipes/{recipe_slug}/add-selected", response_model=RecipeCartAddOut)
def add_selected_recipe_products_to_cart(
    recipe_slug: str,
    payload: RecipeCartAddRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    try:
        return add_selected_recipe_products(
            db,
            current_user.id,
            recipe_slug,
            payload.product_ids,
        )
    except CartServiceError as exc:
        raise _service_error(exc) from exc
