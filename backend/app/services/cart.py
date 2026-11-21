"""Business logic for cart operations and Smart Recipe-to-Cart matching."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.catalog import Product
from app.models.commerce import CartItem
from app.repositories.cart import (
    create_active_cart,
    find_cart_item,
    get_active_cart,
    get_cart_with_items,
    load_available_pantry_ingredient_ids,
    load_available_product_options,
    load_mapped_ingredient_ids,
    load_owned_cart_item,
    load_products_by_ids,
    load_recipe_for_cart_plan,
)
from app.schemas.cart import (
    CartItemOut,
    CartOut,
    MissingIngredientOut,
    MissingProductOut,
    RecipeCartAddOut,
    RecipeCartPlanOut,
)
from app.schemas.catalog import ProductOut
from app.schemas.kitchen import decimal_text
from app.schemas.recipe import RecipeOut

MAX_CART_QUANTITY = 99
QUANTITY_NOTE = (
    "Recipe amounts describe what the recipe needs. Grocery matches are added as "
    "one listed product pack each because the catalogue stores no recipe-to-pack "
    "unit conversion."
)


class CartServiceError(Exception):
    """Base error translated to an HTTP response by the cart API layer."""

    status_code = 400

    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


class CartNotFoundError(CartServiceError):
    status_code = 404


class CartConflictError(CartServiceError):
    status_code = 409


class CartValidationError(CartServiceError):
    status_code = 422


def _money(value: Decimal) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"))


def _empty_cart() -> CartOut:
    return CartOut(
        items=[],
        item_count=0,
        line_count=0,
        total=Decimal("0.00"),
        unavailable_item_count=0,
    )


def _item_out(item: CartItem) -> CartItemOut:
    unit_price = _money(item.product.price)
    return CartItemOut(
        id=item.id,
        product=ProductOut.model_validate(item.product),
        quantity=item.quantity,
        unit_price=unit_price,
        subtotal=_money(unit_price * item.quantity),
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def get_cart(db: Session, user_id: UUID) -> CartOut:
    """Return the user's active cart without creating one for a read-only visit."""
    cart = get_cart_with_items(db, user_id)
    if cart is None or not cart.items:
        return _empty_cart()

    items = sorted(
        (_item_out(item) for item in cart.items),
        key=lambda item: (item.product.name.lower(), str(item.product.id)),
    )
    return CartOut(
        items=items,
        item_count=sum(item.quantity for item in items),
        line_count=len(items),
        total=_money(sum((item.subtotal for item in items), Decimal("0.00"))),
        unavailable_item_count=sum(1 for item in items if not item.product.is_available),
    )


def _get_or_create_cart(db: Session, user_id: UUID):
    cart = get_active_cart(db, user_id)
    if cart is not None:
        return cart
    try:
        return create_active_cart(db, user_id)
    except IntegrityError:
        # Another request may have created the active cart between the read and
        # insert. The partial unique index keeps this safe; reuse the winner.
        db.rollback()
        cart = get_active_cart(db, user_id)
        if cart is None:
            raise CartConflictError("Unable to open your shopping cart")
        return cart


def _reload_item(db: Session, user_id: UUID, item_id: UUID) -> CartItemOut:
    item = load_owned_cart_item(db, user_id, item_id)
    if item is None:
        raise CartNotFoundError("Cart item not found")
    return _item_out(item)


def add_item(db: Session, user_id: UUID, product_id: UUID, quantity: int) -> tuple[CartItemOut, bool]:
    """Add a product, aggregating quantity when it is already in the cart."""
    product = db.get(Product, product_id)
    if product is None:
        raise CartNotFoundError("Product not found")
    if not product.is_available:
        raise CartConflictError("Product is not available")

    cart = _get_or_create_cart(db, user_id)
    existing = find_cart_item(db, cart.id, product_id)

    if existing:
        updated_quantity = existing.quantity + quantity
        if updated_quantity > MAX_CART_QUANTITY:
            raise CartValidationError(f"Cart quantity cannot exceed {MAX_CART_QUANTITY}")
        existing.quantity = updated_quantity
        created = False
        item_id = existing.id
    else:
        item_id = uuid4()
        item = CartItem(id=item_id, cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)
        created = True

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        cart = get_active_cart(db, user_id)
        if cart is None:
            raise CartConflictError("Unable to add product to your cart")
        existing = find_cart_item(db, cart.id, product_id)
        if existing is None:
            raise CartConflictError("Unable to add product to your cart")
        updated_quantity = existing.quantity + quantity
        if updated_quantity > MAX_CART_QUANTITY:
            raise CartValidationError(f"Cart quantity cannot exceed {MAX_CART_QUANTITY}")
        existing.quantity = updated_quantity
        created = False
        item_id = existing.id
        db.commit()

    return _reload_item(db, user_id, item_id), created


def update_item(db: Session, user_id: UUID, item_id: UUID, quantity: int) -> CartItemOut:
    item = load_owned_cart_item(db, user_id, item_id)
    if item is None:
        raise CartNotFoundError("Cart item not found")
    if not item.product.is_available:
        raise CartConflictError("Product is not available")
    item.quantity = quantity
    db.commit()
    return _reload_item(db, user_id, item_id)


def remove_item(db: Session, user_id: UUID, item_id: UUID) -> None:
    item = load_owned_cart_item(db, user_id, item_id)
    if item is None:
        raise CartNotFoundError("Cart item not found")
    db.delete(item)
    db.commit()


def build_recipe_cart_plan(db: Session, user_id: UUID, slug: str) -> RecipeCartPlanOut:
    """Find missing recipe ingredients and their real, available mapped products."""
    recipe = load_recipe_for_cart_plan(db, slug)
    if recipe is None:
        raise CartNotFoundError("Recipe not found")

    links = sorted(recipe.recipe_ingredients, key=lambda link: link.display_order)
    pantry_ids = load_available_pantry_ingredient_ids(db, user_id)
    missing_links = [link for link in links if link.ingredient_id not in pantry_ids]
    missing_ids = {link.ingredient_id for link in missing_links}

    mapped_ids = load_mapped_ingredient_ids(db, missing_ids)
    options_by_ingredient = load_available_product_options(db, missing_ids)

    missing_ingredients: list[MissingIngredientOut] = []
    for link in missing_links:
        options = options_by_ingredient.get(link.ingredient_id, [])
        if options:
            status = "available"
        elif link.ingredient_id in mapped_ids:
            status = "unavailable"
        else:
            status = "unmapped"

        missing_ingredients.append(
            MissingIngredientOut(
                id=link.ingredient_id,
                name=link.ingredient.name,
                quantity=decimal_text(link.quantity),
                unit=link.unit,
                preparation_note=link.preparation_note,
                display_order=link.display_order,
                status=status,
                products=[
                    MissingProductOut(
                        id=product.id,
                        name=product.name,
                        slug=product.slug,
                        price=_money(product.price),
                        unit=product.unit,
                        size=product.size,
                        image_url=product.image_url,
                        match_priority=priority,
                        substitution_note=note,
                        cart_quantity=1,
                    )
                    for product, priority, note in options
                ],
            )
        )

    return RecipeCartPlanOut(
        recipe=RecipeOut.model_validate(recipe),
        missing_ingredients=missing_ingredients,
        required_count=len(links),
        available_pantry_count=len(links) - len(missing_links),
        missing_count=len(missing_links),
        matched_missing_count=sum(1 for item in missing_ingredients if item.status == "available"),
        unmapped_missing_count=sum(1 for item in missing_ingredients if item.status == "unmapped"),
        unavailable_missing_count=sum(1 for item in missing_ingredients if item.status == "unavailable"),
        quantity_note=QUANTITY_NOTE,
    )


def add_selected_recipe_products(
    db: Session,
    user_id: UUID,
    slug: str,
    product_ids: list[UUID],
) -> RecipeCartAddOut:
    """Add only products verified as matches for missing ingredients in this recipe."""
    plan = build_recipe_cart_plan(db, user_id, slug)
    allowed_ids = {
        product.id
        for ingredient in plan.missing_ingredients
        for product in ingredient.products
    }
    requested_ids = set(product_ids)
    invalid_ids = requested_ids - allowed_ids
    if invalid_ids:
        raise CartValidationError("Selected products are not valid matches for this recipe")

    # A product mapped to more than one missing ingredient should be bought once.
    unique_ids = list(dict.fromkeys(product_ids))
    products = load_products_by_ids(db, set(unique_ids))
    if any(product_id not in products for product_id in unique_ids):
        raise CartNotFoundError("Product not found")
    if any(not products[product_id].is_available for product_id in unique_ids):
        raise CartConflictError("One or more selected products are no longer available")

    cart = _get_or_create_cart(db, user_id)
    for product_id in unique_ids:
        existing = find_cart_item(db, cart.id, product_id)
        if existing:
            updated_quantity = existing.quantity + 1
            if updated_quantity > MAX_CART_QUANTITY:
                raise CartValidationError(f"Cart quantity cannot exceed {MAX_CART_QUANTITY}")
            existing.quantity = updated_quantity
        else:
            db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=1))

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CartConflictError("Unable to add selected products to your cart")

    return RecipeCartAddOut(
        cart=get_cart(db, user_id),
        products_added=len(unique_ids),
        added_product_ids=unique_ids,
    )
