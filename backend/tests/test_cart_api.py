import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.auth import AuthenticatedUser, get_authenticated_user
from app.database.session import SessionLocal
from app.main import app
from app.models.catalog import Product, ProductCategory
from app.models.recipe import Ingredient, Recipe

client = TestClient(app)

RECIPE_SLUG = "idli"
UNAVAILABLE_RECIPE_SLUG = "garlic-bread"
SALT_NAME = "Iodized Salt"
URAD_DAL_PRODUCT_NAME = "Urad Dal Whole"


@pytest.fixture(scope="module")
def cart_fixture():
    user_ids = [uuid.uuid4(), uuid.uuid4()]
    available_product_id = uuid.uuid4()
    unavailable_product_id = uuid.uuid4()
    available_slug = f"phase8-test-available-{available_product_id.hex}"
    unavailable_slug = f"phase8-test-unavailable-{unavailable_product_id.hex}"

    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("INSERT INTO auth.users (id) VALUES (:uid)"), {"uid": user_id})

        category_id = db.execute(select(ProductCategory.id).limit(1)).scalar_one()
        idli_rice_ingredient_id = db.execute(
            select(Ingredient.id).where(Ingredient.name == "Idli Rice")
        ).scalar_one()
        garlic_ingredient_id = db.execute(
            select(Ingredient.id).where(Ingredient.name == "Garlic")
        ).scalar_one()

        db.execute(
            text(
                """
                INSERT INTO products
                    (id, category_id, name, slug, price, unit, size, is_available)
                VALUES
                    (:id, :category_id, :name, :slug, :price, :unit, :size, true)
                """
            ),
            {
                "id": available_product_id,
                "category_id": category_id,
                "name": "Phase 8 Alternate Idli Rice",
                "slug": available_slug,
                "price": Decimal("240.00"),
                "unit": "kg",
                "size": "1 kg",
            },
        )
        db.execute(
            text(
                """
                INSERT INTO products
                    (id, category_id, name, slug, price, unit, size, is_available)
                VALUES
                    (:id, :category_id, :name, :slug, :price, :unit, :size, false)
                """
            ),
            {
                "id": unavailable_product_id,
                "category_id": category_id,
                "name": "Phase 8 Unavailable Garlic",
                "slug": unavailable_slug,
                "price": Decimal("99.00"),
                "unit": "g",
                "size": "100 g",
            },
        )
        db.execute(
            text(
                """
                INSERT INTO product_ingredient_mappings
                    (id, product_id, ingredient_id, match_priority)
                VALUES
                    (:id, :product_id, :ingredient_id, :priority)
                """
            ),
            {
                "id": uuid.uuid4(),
                "product_id": available_product_id,
                "ingredient_id": idli_rice_ingredient_id,
                "priority": 50,
            },
        )
        db.execute(
            text(
                """
                INSERT INTO product_ingredient_mappings
                    (id, product_id, ingredient_id, match_priority)
                VALUES
                    (:id, :product_id, :ingredient_id, :priority)
                """
            ),
            {
                "id": uuid.uuid4(),
                "product_id": unavailable_product_id,
                "ingredient_id": garlic_ingredient_id,
                "priority": 50,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    yield {
        "user_ids": user_ids,
        "available_product_id": available_product_id,
        "unavailable_product_id": unavailable_product_id,
    }

    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("DELETE FROM shopping_carts WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM auth.users WHERE id = :uid"), {"uid": user_id})
        for product_id in (available_product_id, unavailable_product_id):
            db.execute(
                text("DELETE FROM product_ingredient_mappings WHERE product_id = :pid"),
                {"pid": product_id},
            )
            db.execute(text("DELETE FROM products WHERE id = :pid"), {"pid": product_id})
        db.commit()
    finally:
        db.close()


def use_user(user_id):
    app.dependency_overrides[get_authenticated_user] = lambda uid=user_id: AuthenticatedUser(
        id=uid, email="phase8-cart@example.test"
    )


def clear_cart_state(user_ids):
    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("DELETE FROM shopping_carts WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
        db.commit()
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_cart_state(cart_fixture):
    clear_cart_state(cart_fixture["user_ids"])
    use_user(cart_fixture["user_ids"][0])
    yield
    app.dependency_overrides.pop(get_authenticated_user, None)
    clear_cart_state(cart_fixture["user_ids"])


def product_by_name(name: str):
    with SessionLocal() as db:
        product = db.execute(select(Product).where(Product.name == name)).scalars().one()
        return {"id": str(product.id), "name": product.name, "price": str(product.price)}


def ingredient_id_by_name(name: str) -> str:
    with SessionLocal() as db:
        return str(db.execute(select(Ingredient.id).where(Ingredient.name == name)).scalar_one())


def recipe_id_by_slug(slug: str) -> str:
    with SessionLocal() as db:
        return str(db.execute(select(Recipe.id).where(Recipe.slug == slug)).scalar_one())


def add_to_cart(product_id: str, quantity: int = 1):
    return client.post("/api/cart/items", json={"product_id": product_id, "quantity": quantity})


def get_cart():
    res = client.get("/api/cart")
    assert res.status_code == 200, res.text
    return res.json()


def get_plan(slug: str = RECIPE_SLUG):
    res = client.get(f"/api/cart/recipes/{slug}/plan")
    assert res.status_code == 200, res.text
    return res.json()


def add_pantry(ingredient_name: str):
    res = client.post(
        "/api/kitchen/pantry",
        json={"ingredient_id": ingredient_id_by_name(ingredient_name), "is_available": True},
    )
    assert res.status_code == 201, res.text
    return res.json()


def test_cart_requires_authentication():
    app.dependency_overrides.pop(get_authenticated_user, None)
    res = client.get("/api/cart")
    assert res.status_code == 401
    assert res.json().get("detail") == "Authentication required"


def test_empty_cart_does_not_create_a_cart_row(cart_fixture):
    assert get_cart() == {
        "items": [],
        "item_count": 0,
        "line_count": 0,
        "total": "0.00",
        "unavailable_item_count": 0,
    }
    with SessionLocal() as db:
        count = db.execute(
            text("SELECT count(*) FROM shopping_carts WHERE user_id = :uid"),
            {"uid": cart_fixture["user_ids"][0]},
        ).scalar_one()
    assert count == 0


def test_add_duplicate_product_updates_quantity_and_uses_current_db_price(cart_fixture):
    product = product_by_name(SALT_NAME)
    temp_id = str(cart_fixture["available_product_id"])

    created = add_to_cart(product["id"], 1)
    assert created.status_code == 201, created.text
    assert created.json()["unit_price"] == product["price"]
    assert created.json()["subtotal"] == product["price"]

    spam_price = add_to_cart(product["id"], 2)
    assert spam_price.status_code == 200, spam_price.text
    assert spam_price.json()["quantity"] == 3

    cart = get_cart()
    assert cart["line_count"] == 1
    assert cart["item_count"] == 3
    assert Decimal(cart["total"]) == Decimal(product["price"]) * 3
    assert cart["items"][0]["id"] == created.json()["id"]

    added = add_to_cart(temp_id, 1)
    assert added.status_code == 201, added.text
    with SessionLocal() as db:
        db.execute(
            text("UPDATE products SET price = :price WHERE id = :pid"),
            {"price": Decimal("777.77"), "pid": cart_fixture["available_product_id"]},
        )
        db.commit()
    try:
        refreshed = get_cart()
        option = next(item for item in refreshed["items"] if item["product"]["id"] == temp_id)
        assert option["unit_price"] == "777.77"
        assert option["subtotal"] == "777.77"
        assert Decimal(refreshed["total"]) == Decimal(product["price"]) * 3 + Decimal("777.77")
    finally:
        with SessionLocal() as db:
            db.execute(
                text("UPDATE products SET price = :price WHERE id = :pid"),
                {"price": Decimal("240.00"), "pid": cart_fixture["available_product_id"]},
            )
            db.commit()


def test_update_and_remove_cart_item():
    product = product_by_name(SALT_NAME)
    item = add_to_cart(product["id"]).json()

    updated = client.patch(f"/api/cart/items/{item['id']}", json={"quantity": 5})
    assert updated.status_code == 200, updated.text
    assert updated.json()["quantity"] == 5
    assert updated.json()["subtotal"] == str(Decimal(product["price"]) * 5)
    assert get_cart()["item_count"] == 5

    removed = client.delete(f"/api/cart/items/{item['id']}")
    assert removed.status_code == 204
    assert get_cart()["items"] == []
    assert client.delete(f"/api/cart/items/{item['id']}").status_code == 404


def test_invalid_and_unavailable_products_and_quantities(cart_fixture):
    product = product_by_name(SALT_NAME)

    missing = add_to_cart(str(uuid.uuid4()))
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Product not found"

    unavailable = add_to_cart(str(cart_fixture["unavailable_product_id"]))
    assert unavailable.status_code == 409
    assert unavailable.json()["detail"] == "Product is not available"

    for quantity in (0, -1, 100):
        res = add_to_cart(product["id"], quantity)
        assert res.status_code == 422, res.text

    spoofed = client.post(
        "/api/cart/items",
        json={
            "product_id": product["id"],
            "quantity": 1,
            "user_id": str(cart_fixture["user_ids"][1]),
        },
    )
    assert spoofed.status_code == 422

    client_supplied_price = client.post(
        "/api/cart/items",
        json={"product_id": product["id"], "quantity": 1, "price": "0.01"},
    )
    assert client_supplied_price.status_code == 422

    item = add_to_cart(product["id"]).json()
    assert client.patch(f"/api/cart/items/{item['id']}", json={"quantity": 0}).status_code == 422
    assert get_cart()["item_count"] == 1


def test_cart_items_are_scoped_to_authenticated_user(cart_fixture):
    user_ids = cart_fixture["user_ids"]
    product = product_by_name(SALT_NAME)
    item = add_to_cart(product["id"]).json()

    use_user(user_ids[1])
    assert get_cart()["items"] == []
    assert client.patch(f"/api/cart/items/{item['id']}", json={"quantity": 9}).status_code == 404
    assert client.delete(f"/api/cart/items/{item['id']}").status_code == 404

    use_user(user_ids[0])
    assert get_cart()["item_count"] == 1


def test_recipe_plan_excludes_pantry_ingredients_and_reports_unmapped_items():
    add_pantry("Idli Rice")
    plan = get_plan()

    assert plan["recipe"]["id"] == recipe_id_by_slug(RECIPE_SLUG)
    assert plan["available_pantry_count"] == 1
    assert plan["missing_count"] == 3
    assert plan["required_count"] == len(plan["missing_ingredients"]) + 1
    assert [item["name"] for item in plan["missing_ingredients"]] == [
        "Urad Dal",
        "Fenugreek Seeds",
        "Salt",
    ]

    urad = next(item for item in plan["missing_ingredients"] if item["name"] == "Urad Dal")
    assert urad["status"] == "available"
    assert any(product["name"] == URAD_DAL_PRODUCT_NAME for product in urad["products"])
    assert all(product["cart_quantity"] == 1 for product in urad["products"])

    fenugreek = next(item for item in plan["missing_ingredients"] if item["name"] == "Fenugreek Seeds")
    assert fenugreek["status"] == "unmapped"
    assert fenugreek["products"] == []
    assert plan["unmapped_missing_count"] == 1
    assert plan["unavailable_missing_count"] == 0
    assert "one listed product pack" in plan["quantity_note"]

    all_product_names = {
        product["name"]
        for ingredient in plan["missing_ingredients"]
        for product in ingredient["products"]
    }
    assert "Idli Rice" not in all_product_names


def test_recipe_plan_shows_multiple_options_and_unavailable_mappings():
    plan = get_plan()
    idli_rice = next(item for item in plan["missing_ingredients"] if item["name"] == "Idli Rice")
    assert idli_rice["status"] == "available"
    assert len(idli_rice["products"]) == 2
    assert idli_rice["products"][0]["name"] == "Phase 8 Alternate Idli Rice"
    assert [item["name"] for item in idli_rice["products"]] == [
        "Phase 8 Alternate Idli Rice",
        "Idli Rice",
    ]

    garlic_plan = get_plan(UNAVAILABLE_RECIPE_SLUG)
    garlic = next(item for item in garlic_plan["missing_ingredients"] if item["name"] == "Garlic")
    assert garlic["status"] == "unavailable"
    assert garlic["products"] == []
    assert garlic_plan["unavailable_missing_count"] == 1

    baguette = next(item for item in garlic_plan["missing_ingredients"] if item["name"] == "Baguette")
    assert baguette["status"] == "unmapped"
    assert baguette["products"] == []


def test_add_selected_recipe_products_validates_matches_and_updates_cart():
    plan = get_plan()
    rice = next(item for item in plan["missing_ingredients"] if item["name"] == "Idli Rice")
    urad = next(item for item in plan["missing_ingredients"] if item["name"] == "Urad Dal")
    selected_ids = [rice["products"][0]["id"], urad["products"][0]["id"]]

    result = client.post(
        f"/api/cart/recipes/{RECIPE_SLUG}/add-selected",
        json={"product_ids": selected_ids},
    )
    assert result.status_code == 200, result.text
    assert result.json()["products_added"] == 2
    assert set(result.json()["added_product_ids"]) == set(selected_ids)
    cart = result.json()["cart"]
    assert cart["line_count"] == 2
    assert all(item["quantity"] == 1 for item in cart["items"])

    duplicate = client.post(
        f"/api/cart/recipes/{RECIPE_SLUG}/add-selected",
        json={"product_ids": [selected_ids[0], selected_ids[0]]},
    )
    assert duplicate.status_code == 200, duplicate.text
    assert duplicate.json()["products_added"] == 1
    assert next(
        item for item in duplicate.json()["cart"]["items"] if item["product"]["id"] == selected_ids[0]
    )["quantity"] == 2

    before = get_cart()
    invalid = client.post(
        f"/api/cart/recipes/{RECIPE_SLUG}/add-selected",
        json={"product_ids": [str(uuid.uuid4())]},
    )
    assert invalid.status_code == 422
    assert get_cart() == before

    add_pantry("Idli Rice")
    pantry_plan = get_plan()
    assert "Idli Rice" not in [item["name"] for item in pantry_plan["missing_ingredients"]]
    excluded = client.post(
        f"/api/cart/recipes/{RECIPE_SLUG}/add-selected",
        json={"product_ids": [selected_ids[0]]},
    )
    assert excluded.status_code == 422
