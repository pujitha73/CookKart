"""Authenticated My Kitchen APIs: pantry and saved recipes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.api.recipes import MealType
from app.core.auth import CurrentUser
from app.database.session import get_db
from app.models.personalization import SavedRecipe, UserPantry
from app.models.recipe import Ingredient, Recipe
from app.schemas.kitchen import (
    IngredientOut,
    PantryEntryCreate,
    PantryEntryOut,
    PantryEntryUpdate,
    SavedRecipeCreate,
    SavedRecipeOut,
    decimal_text,
)
from app.schemas.recommendations import RecommendationListOut
from app.schemas.recipe import RecipeOut
from app.services.recommendations import build_recommendations

router = APIRouter(prefix="/kitchen", tags=["kitchen"])


def _not_found(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def _pantry_out(entry: UserPantry) -> PantryEntryOut:
    return PantryEntryOut(
        id=entry.id,
        ingredient=IngredientOut.model_validate(entry.ingredient),
        quantity=decimal_text(entry.quantity),
        unit=entry.unit,
        is_available=entry.is_available,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


def _saved_out(entry: SavedRecipe) -> SavedRecipeOut:
    return SavedRecipeOut(
        id=entry.id,
        recipe=RecipeOut.model_validate(entry.recipe),
        saved_at=entry.created_at,
    )


def _load_pantry_entry(db: Session, user_id, entry_id) -> UserPantry:
    entry = db.execute(
        select(UserPantry)
        .options(joinedload(UserPantry.ingredient))
        .where(UserPantry.id == entry_id, UserPantry.user_id == user_id)
    ).scalars().unique().first()
    if not entry:
        raise _not_found("Pantry entry not found")
    return entry


def _load_saved_entry(db: Session, user_id, recipe_id) -> SavedRecipe:
    entry = db.execute(
        select(SavedRecipe)
        .options(joinedload(SavedRecipe.recipe).joinedload(Recipe.collection))
        .where(SavedRecipe.user_id == user_id, SavedRecipe.recipe_id == recipe_id)
    ).scalars().unique().first()
    if not entry:
        raise _not_found("Saved recipe not found")
    return entry


@router.get("/ingredients", response_model=list[IngredientOut])
def list_ingredients(
    _current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    rows = db.execute(select(Ingredient).order_by(Ingredient.name.asc())).scalars().all()
    return [IngredientOut.model_validate(row) for row in rows]


@router.get("/recommendations", response_model=RecommendationListOut)
def list_recommendations(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
    meal_type: MealType | None = Query(None),
    collection: str | None = Query(None, description="Collection slug"),
):
    return build_recommendations(
        db,
        current_user.id,
        meal_type=meal_type,
        collection=collection,
    )


@router.get("/pantry", response_model=list[PantryEntryOut])
def list_pantry(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    entries = db.execute(
        select(UserPantry)
        .options(joinedload(UserPantry.ingredient))
        .where(UserPantry.user_id == current_user.id)
        .order_by(UserPantry.created_at.asc())
    ).scalars().unique().all()
    return [_pantry_out(entry) for entry in entries]


@router.post("/pantry", response_model=PantryEntryOut, status_code=status.HTTP_201_CREATED)
def add_pantry_item(
    payload: PantryEntryCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    ingredient = db.get(Ingredient, payload.ingredient_id)
    if not ingredient:
        raise _not_found("Ingredient not found")

    duplicate = db.execute(
        select(UserPantry.id).where(
            UserPantry.user_id == current_user.id,
            UserPantry.ingredient_id == payload.ingredient_id,
        )
    ).scalar_one_or_none()
    if duplicate:
        raise _conflict("Ingredient is already in your pantry")

    entry = UserPantry(
        user_id=current_user.id,
        ingredient_id=payload.ingredient_id,
        quantity=payload.quantity,
        unit=payload.unit,
        is_available=payload.is_available,
    )
    db.add(entry)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _conflict("Ingredient is already in your pantry") from exc

    entry = _load_pantry_entry(db, current_user.id, entry.id)
    return _pantry_out(entry)


@router.patch("/pantry/{entry_id}", response_model=PantryEntryOut)
def update_pantry_item(
    entry_id: UUID,
    payload: PantryEntryUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    fields = payload.model_fields_set
    if not fields:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="At least one pantry field must be supplied",
        )
    if "is_available" in fields and payload.is_available is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="is_available must be true or false",
        )

    entry = _load_pantry_entry(db, current_user.id, entry_id)
    if "quantity" in fields:
        entry.quantity = payload.quantity
    if "unit" in fields:
        entry.unit = payload.unit
    if "is_available" in fields:
        entry.is_available = payload.is_available
    db.commit()
    db.refresh(entry)
    return _pantry_out(entry)


@router.delete("/pantry/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_pantry_item(
    entry_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    entry = _load_pantry_entry(db, current_user.id, entry_id)
    db.delete(entry)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/saved-recipes", response_model=list[SavedRecipeOut])
def list_saved_recipes(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    entries = db.execute(
        select(SavedRecipe)
        .options(joinedload(SavedRecipe.recipe).joinedload(Recipe.collection))
        .where(SavedRecipe.user_id == current_user.id)
        .order_by(SavedRecipe.created_at.asc())
    ).scalars().unique().all()
    return [_saved_out(entry) for entry in entries]


@router.post(
    "/saved-recipes",
    response_model=SavedRecipeOut,
    status_code=status.HTTP_201_CREATED,
)
def save_recipe(
    payload: SavedRecipeCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    recipe = db.get(Recipe, payload.recipe_id)
    if not recipe:
        raise _not_found("Recipe not found")

    duplicate = db.execute(
        select(SavedRecipe.id).where(
            SavedRecipe.user_id == current_user.id,
            SavedRecipe.recipe_id == payload.recipe_id,
        )
    ).scalar_one_or_none()
    if duplicate:
        raise _conflict("Recipe is already saved")

    entry = SavedRecipe(user_id=current_user.id, recipe_id=payload.recipe_id)
    db.add(entry)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise _conflict("Recipe is already saved") from exc

    entry = _load_saved_entry(db, current_user.id, payload.recipe_id)
    return _saved_out(entry)


@router.delete("/saved-recipes/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def unsave_recipe(
    recipe_id: UUID,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
):
    entry = _load_saved_entry(db, current_user.id, recipe_id)
    db.delete(entry)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
