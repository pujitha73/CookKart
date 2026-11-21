"""Database queries for shopping carts and recipe-to-cart matching."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.catalog import Product
from app.models.commerce import CartItem, ShoppingCart
from app.models.mapping import ProductIngredientMapping
from app.models.personalization import UserPantry
from app.models.recipe import Recipe, RecipeIngredient


def get_active_cart(db: Session, user_id: UUID) -> ShoppingCart | None:
    return db.execute(
        select(ShoppingCart).where(
            ShoppingCart.user_id == user_id,
            ShoppingCart.status == "active",
        )
    ).scalars().first()


def create_active_cart(db: Session, user_id: UUID) -> ShoppingCart:
    cart = ShoppingCart(user_id=user_id, status="active")
    db.add(cart)
    db.flush()
    return cart


def get_cart_with_items(db: Session, user_id: UUID) -> ShoppingCart | None:
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
        )
        .scalars()
        .unique()
        .first()
    )


def find_cart_item(db: Session, cart_id: UUID, product_id: UUID) -> CartItem | None:
    return db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart_id,
            CartItem.product_id == product_id,
        )
    ).scalars().first()


def load_owned_cart_item(db: Session, user_id: UUID, item_id: UUID) -> CartItem | None:
    return (
        db.execute(
            select(CartItem)
            .join(ShoppingCart, CartItem.cart_id == ShoppingCart.id)
            .options(joinedload(CartItem.product).joinedload(Product.category))
            .where(
                CartItem.id == item_id,
                ShoppingCart.user_id == user_id,
                ShoppingCart.status == "active",
            )
        )
        .scalars()
        .unique()
        .first()
    )


def load_recipe_for_cart_plan(db: Session, slug: str) -> Recipe | None:
    return (
        db.execute(
            select(Recipe)
            .options(
                joinedload(Recipe.collection),
                selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
            )
            .where(Recipe.slug == slug)
        )
        .scalars()
        .unique()
        .first()
    )


def load_available_pantry_ingredient_ids(db: Session, user_id: UUID) -> set[UUID]:
    return set(
        db.execute(
            select(UserPantry.ingredient_id).where(
                UserPantry.user_id == user_id,
                UserPantry.is_available.is_(True),
            )
        )
        .scalars()
        .all()
    )


def load_mapped_ingredient_ids(db: Session, ingredient_ids: set[UUID]) -> set[UUID]:
    if not ingredient_ids:
        return set()
    return set(
        db.execute(
            select(ProductIngredientMapping.ingredient_id).where(
                ProductIngredientMapping.ingredient_id.in_(ingredient_ids)
            )
        )
        .scalars()
        .all()
    )


def load_available_product_options(
    db: Session, ingredient_ids: set[UUID]
) -> dict[UUID, list[tuple[Product, int, str | None]]]:
    """Return available mapped products per ingredient, best match first."""
    if not ingredient_ids:
        return {}

    rows = (
        db.execute(
            select(
                ProductIngredientMapping.ingredient_id,
                Product,
                ProductIngredientMapping.match_priority,
                ProductIngredientMapping.substitution_note,
            )
            .join(Product, ProductIngredientMapping.product_id == Product.id)
            .options(joinedload(Product.category))
            .where(
                ProductIngredientMapping.ingredient_id.in_(ingredient_ids),
                Product.is_available.is_(True),
            )
            .order_by(
                ProductIngredientMapping.match_priority.asc(),
                Product.name.asc(),
            )
        )
        .unique()
        .all()
    )

    options: dict[UUID, list[tuple[Product, int, str | None]]] = {id_: [] for id_ in ingredient_ids}
    for ingredient_id, product, priority, note in rows:
        options[ingredient_id].append((product, priority, note))
    return options


def load_products_by_ids(db: Session, product_ids: set[UUID]) -> dict[UUID, Product]:
    if not product_ids:
        return {}
    rows = (
        db.execute(
            select(Product)
            .options(joinedload(Product.category))
            .where(Product.id.in_(product_ids))
        )
        .scalars()
        .unique()
        .all()
    )
    return {product.id: product for product in rows}
