"""Database queries for pantry-based recipe recommendations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.personalization import UserPantry
from app.models.recipe import Recipe, RecipeCollection, RecipeIngredient


def load_recommendation_data(
    db: Session,
    user_id: UUID,
    meal_type: str | None = None,
    collection: str | None = None,
) -> tuple[set[UUID], list[Recipe]]:
    """Return available pantry ingredient IDs and recipe candidates.

    Availability is scoped to the authenticated user and read directly from
    ``user_pantry``. Recipe ingredients are eagerly loaded so scoring does not
    issue a query per recipe.
    """
    available_ids = set(
        db.execute(
            select(UserPantry.ingredient_id).where(
                UserPantry.user_id == user_id,
                UserPantry.is_available.is_(True),
            )
        )
        .scalars()
        .all()
    )

    filters = []
    if meal_type:
        filters.append(Recipe.meal_type == meal_type)
    if collection:
        filters.append(Recipe.collection.has(RecipeCollection.slug == collection))

    stmt = (
        select(Recipe)
        .options(
            joinedload(Recipe.collection),
            selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
        )
        .where(*filters)
        .order_by(Recipe.name.asc())
    )
    recipes = db.execute(stmt).scalars().unique().all()
    return available_ids, list(recipes)
