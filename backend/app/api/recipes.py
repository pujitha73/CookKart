from math import ceil
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database.session import get_db
from app.models.recipe import Recipe, RecipeCollection, RecipeIngredient
from app.schemas.recipe import (
    RecipeCollectionOut,
    RecipeDetailOut,
    RecipeListOut,
    RecipeOut,
    ingredient_out,
    parse_instructions,
)
from app.utils.search import ilike_contains

router = APIRouter(prefix="/recipes", tags=["recipes"])

MealType = Literal["breakfast-tiffin", "lunch-dinner", "snack"]


@router.get("/collections", response_model=list[RecipeCollectionOut])
def list_collections(db: Session = Depends(get_db)):
    counts = dict(
        db.execute(select(Recipe.collection_id, func.count(Recipe.id)).group_by(Recipe.collection_id)).all()
    )
    collections = db.execute(select(RecipeCollection).order_by(RecipeCollection.name.asc())).scalars().all()
    return [
        RecipeCollectionOut.model_validate(collection).model_copy(
            update={"recipe_count": counts.get(collection.id, 0)}
        )
        for collection in collections
    ]


@router.get("", response_model=RecipeListOut)
def list_recipes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
    collection: str | None = Query(None, description="Collection slug"),
    meal_type: MealType | None = Query(None),
    search: str | None = Query(None, description="Search by recipe name"),
):
    filters = []
    if collection:
        filters.append(Recipe.collection.has(RecipeCollection.slug == collection))
    if meal_type:
        filters.append(Recipe.meal_type == meal_type)
    if search:
        name_filter = ilike_contains(Recipe.name, search)
        if name_filter is not None:
            filters.append(name_filter)

    base = select(Recipe).options(joinedload(Recipe.collection)).where(*filters)
    count_stmt = select(func.count()).select_from(select(Recipe.id).where(*filters).subquery())
    total = db.execute(count_stmt).scalar_one()

    stmt = base.order_by(Recipe.name.asc()).offset((page - 1) * page_size).limit(page_size)
    items = db.execute(stmt).scalars().unique().all()
    pages = ceil(total / page_size) if total else 0
    return RecipeListOut(
        items=[RecipeOut.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get("/{slug}", response_model=RecipeDetailOut)
def get_recipe(slug: str, db: Session = Depends(get_db)):
    stmt = (
        select(Recipe)
        .options(
            joinedload(Recipe.collection),
            selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
        )
        .where(Recipe.slug == slug)
    )
    recipe = db.execute(stmt).scalars().unique().first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    base = RecipeOut.model_validate(recipe).model_dump()
    links = sorted(recipe.recipe_ingredients, key=lambda link: link.display_order)
    return RecipeDetailOut(
        **base,
        instructions=parse_instructions(recipe.instructions),
        ingredients=[ingredient_out(link) for link in links],
    )
