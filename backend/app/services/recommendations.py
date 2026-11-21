"""Business logic for pantry-based recipe recommendations."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.recipe import RecipeIngredient
from app.repositories.recommendations import load_recommendation_data
from app.schemas.kitchen import decimal_text
from app.schemas.recommendations import (
    RecommendedIngredientOut,
    RecipeRecommendationOut,
    RecommendationListOut,
)
from app.schemas.recipe import RecipeOut


def _ingredient_out(link: RecipeIngredient) -> RecommendedIngredientOut:
    return RecommendedIngredientOut(
        id=link.ingredient.id,
        name=link.ingredient.name,
        quantity=decimal_text(link.quantity),
        unit=link.unit,
        display_order=link.display_order,
    )


def build_recommendations(
    db: Session,
    user_id: UUID,
    meal_type: str | None = None,
    collection: str | None = None,
) -> RecommendationListOut:
    """Rank recipes by the share of required ingredients available in the pantry.

    Matching uses canonical ingredient IDs only. Recipes with no available
    matches are omitted, and missing ingredients are always returned so the UI
    cannot present a partial match as fully prepared.
    """
    available_ids, recipes = load_recommendation_data(db, user_id, meal_type, collection)
    ranked: list[tuple[float, RecipeRecommendationOut]] = []

    for recipe in recipes:
        links = sorted(recipe.recipe_ingredients, key=lambda link: link.display_order)
        required_count = len(links)
        if required_count == 0:
            continue

        available = [link for link in links if link.ingredient_id in available_ids]
        if not available:
            continue

        missing = [link for link in links if link.ingredient_id not in available_ids]
        ratio = len(available) / required_count
        ranked.append(
            (
                ratio,
                RecipeRecommendationOut(
                    recipe=RecipeOut.model_validate(recipe),
                    match_percentage=round(ratio * 100, 1),
                    available_ingredients=[_ingredient_out(link) for link in available],
                    missing_ingredients=[_ingredient_out(link) for link in missing],
                    matched_count=len(available),
                    required_count=required_count,
                    missing_count=len(missing),
                ),
            )
        )

    ranked.sort(key=lambda entry: (-entry[0], entry[1].missing_count, entry[1].recipe.name.lower()))
    items = [item for _, item in ranked]
    return RecommendationListOut(
        items=items,
        total=len(items),
        available_ingredient_count=len(available_ids),
    )
