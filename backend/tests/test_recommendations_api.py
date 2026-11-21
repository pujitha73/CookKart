import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.orm import joinedload, selectinload

from app.core.auth import AuthenticatedUser, get_authenticated_user
from app.database.session import SessionLocal
from app.main import app
from app.models.recipe import Ingredient, Recipe, RecipeIngredient

client = TestClient(app)

IDLI = "Idli"
GARLIC_BREAD = "Garlic Bread"
SALT = "Salt"


@pytest.fixture(scope="module")
def recommendation_users():
    user_ids = [uuid.uuid4(), uuid.uuid4()]
    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("DELETE FROM saved_recipes WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("INSERT INTO auth.users (id) VALUES (:uid)"), {"uid": user_id})
        db.commit()
        yield user_ids
    finally:
        for user_id in user_ids:
            db.execute(text("DELETE FROM saved_recipes WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM auth.users WHERE id = :uid"), {"uid": user_id})
        db.commit()
        db.close()


def _clear_pantry(user_ids):
    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
        db.commit()
    finally:
        db.close()


def _use_user(user_id):
    app.dependency_overrides[get_authenticated_user] = lambda uid=user_id: AuthenticatedUser(
        id=uid, email="phase7-recommendations@example.test"
    )


@pytest.fixture(autouse=True)
def clean_recommendation_state(recommendation_users):
    _clear_pantry(recommendation_users)
    _use_user(recommendation_users[0])
    yield
    app.dependency_overrides.pop(get_authenticated_user, None)
    _clear_pantry(recommendation_users)


def _recipe_details(name: str):
    with SessionLocal() as db:
        recipe = db.execute(
            select(Recipe)
            .options(
                joinedload(Recipe.collection),
                selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
            )
            .where(Recipe.name == name)
        ).scalars().unique().one()
        return {
            "id": str(recipe.id),
            "name": recipe.name,
            "meal_type": recipe.meal_type,
            "collection_slug": recipe.collection.slug,
            "ingredients": [
                {
                    "id": str(link.ingredient_id),
                    "name": link.ingredient.name,
                    "display_order": link.display_order,
                }
                for link in sorted(recipe.recipe_ingredients, key=lambda link: link.display_order)
            ],
        }


def _ingredient_id(name: str) -> str:
    with SessionLocal() as db:
        return str(db.execute(select(Ingredient.id).where(Ingredient.name == name)).scalar_one())


def _add(ingredient_id: str, available: bool = True):
    res = client.post(
        "/api/kitchen/pantry",
        json={"ingredient_id": ingredient_id, "is_available": available},
    )
    assert res.status_code == 201, res.text
    return res.json()


def _recommendations(params: dict | None = None):
    res = client.get("/api/kitchen/recommendations", params=params)
    assert res.status_code == 200, res.text
    return res.json()


def _item_for(data: dict, recipe_id: str):
    return next(
        (item for item in data["items"] if item["recipe"]["id"] == recipe_id),
        None,
    )


def test_empty_pantry_returns_no_recommendations():
    assert _recommendations() == {"items": [], "total": 0, "available_ingredient_count": 0}


def test_match_percentage_and_ingredient_lists_use_real_recipe_data():
    details = _recipe_details(IDLI)
    selected = details["ingredients"][:2]
    for ingredient in selected:
        _add(ingredient["id"])

    data = _recommendations()
    item = _item_for(data, details["id"])
    assert item is not None
    assert data["available_ingredient_count"] == 2
    assert item["matched_count"] == 2
    assert item["required_count"] == len(details["ingredients"])
    assert item["missing_count"] == len(details["ingredients"]) - 2
    assert item["match_percentage"] == round(100 * 2 / len(details["ingredients"]), 1)
    assert [entry["id"] for entry in item["available_ingredients"]] == [
        entry["id"] for entry in selected
    ]
    assert [entry["name"] for entry in item["available_ingredients"]] == [
        entry["name"] for entry in selected
    ]
    assert [entry["id"] for entry in item["missing_ingredients"]] == [
        entry["id"] for entry in details["ingredients"][2:]
    ]
    assert item["missing_count"] == len(item["missing_ingredients"])
    assert item["available_ingredients"] and item["missing_ingredients"]


def test_unavailable_pantry_ingredients_are_ignored():
    details = _recipe_details(IDLI)
    entries = [_add(ingredient["id"]) for ingredient in details["ingredients"]]

    full = _item_for(_recommendations(), details["id"])
    assert full["match_percentage"] == 100.0
    assert full["missing_ingredients"] == []

    disabled = client.patch(
        f"/api/kitchen/pantry/{entries[0]['id']}", json={"is_available": False}
    )
    assert disabled.status_code == 200

    data = _recommendations()
    item = _item_for(data, details["id"])
    assert data["available_ingredient_count"] == len(details["ingredients"]) - 1
    assert item["matched_count"] == len(details["ingredients"]) - 1
    assert item["missing_count"] == 1
    assert item["match_percentage"] == round(100 * (len(details["ingredients"]) - 1) / len(details["ingredients"]), 1)
    assert [entry["id"] for entry in item["missing_ingredients"]] == [
        details["ingredients"][0]["id"]
    ]
    assert details["ingredients"][0]["id"] not in [
        entry["id"] for entry in item["available_ingredients"]
    ]


def test_zero_match_recipes_are_omitted():
    ingredient_id = _ingredient_id("Idli Rice")
    _add(ingredient_id)

    data = _recommendations()
    assert [item["recipe"]["name"] for item in data["items"]] == [IDLI]
    assert all(item["matched_count"] > 0 for item in data["items"])


def test_recommendations_are_sorted_by_highest_match_percentage():
    idli = _recipe_details(IDLI)
    garlic = _recipe_details(GARLIC_BREAD)
    salt_id = _ingredient_id(SALT)

    for ingredient in idli["ingredients"]:
        _add(ingredient["id"])
    non_salt_garlic = [entry for entry in garlic["ingredients"] if entry["id"] != salt_id]
    for ingredient in non_salt_garlic[:3]:
        _add(ingredient["id"])

    data = _recommendations()
    assert len(data["items"]) >= 2
    assert [item["recipe"]["name"] for item in data["items"][:2]] == [IDLI, GARLIC_BREAD]
    assert [item["match_percentage"] for item in data["items"][:2]] == [100.0, 80.0]
    percentages = [item["match_percentage"] for item in data["items"]]
    assert percentages == sorted(percentages, reverse=True)


def test_meal_type_and_collection_filters_are_applied():
    for ingredient in _recipe_details(IDLI)["ingredients"]:
        _add(ingredient["id"])

    lunch = _recommendations({"meal_type": "lunch-dinner"})
    assert lunch["items"]
    assert all(item["recipe"]["meal_type"] == "lunch-dinner" for item in lunch["items"])
    assert IDLI not in [item["recipe"]["name"] for item in lunch["items"]]

    italian = _recommendations({"collection": "italian"})
    assert italian["items"]
    assert all(item["recipe"]["collection"]["slug"] == "italian" for item in italian["items"])
    assert IDLI not in [item["recipe"]["name"] for item in italian["items"]]

    snack_south = _recommendations({"meal_type": "snack", "collection": "south-indian"})
    assert all(
        item["recipe"]["meal_type"] == "snack"
        and item["recipe"]["collection"]["slug"] == "south-indian"
        for item in snack_south["items"]
    )

    no_match = _recommendations({"collection": "not-a-real-collection"})
    assert no_match["items"] == []


def test_pantry_changes_update_the_next_recommendation_fetch():
    details = _recipe_details(IDLI)
    first, second = details["ingredients"][:2]
    first_entry = _add(first["id"])
    second_entry = _add(second["id"])

    partial = _item_for(_recommendations(), details["id"])
    assert partial["match_percentage"] == round(100 * 2 / len(details["ingredients"]), 1)

    disabled = client.patch(
        f"/api/kitchen/pantry/{first_entry['id']}", json={"is_available": False}
    )
    assert disabled.status_code == 200
    after_disable = _item_for(_recommendations(), details["id"])
    assert after_disable["match_percentage"] == round(100 / len(details["ingredients"]), 1)
    assert [entry["id"] for entry in after_disable["available_ingredients"]] == [second["id"]]

    removed = client.delete(f"/api/kitchen/pantry/{second_entry['id']}")
    assert removed.status_code == 204
    assert _recommendations() == {"items": [], "total": 0, "available_ingredient_count": 0}


def test_recommendations_are_scoped_to_authenticated_user(recommendation_users):
    details = _recipe_details(IDLI)
    for ingredient in details["ingredients"][:2]:
        _add(ingredient["id"])

    first_user = _recommendations()
    assert _item_for(first_user, details["id"]) is not None
    assert first_user["available_ingredient_count"] == 2

    _use_user(recommendation_users[1])
    second_user = _recommendations()
    assert second_user["items"] == []
    assert second_user["available_ingredient_count"] == 0

    spoofed = _recommendations({"user_id": str(recommendation_users[0])})
    assert spoofed["items"] == []
    assert spoofed["available_ingredient_count"] == 0

    _use_user(recommendation_users[0])
    still_first_user = _recommendations({"user_id": str(recommendation_users[1])})
    assert _item_for(still_first_user, details["id"]) is not None
    assert still_first_user["available_ingredient_count"] == 2


def test_recommendations_require_authentication():
    app.dependency_overrides.pop(get_authenticated_user, None)
    res = client.get("/api/kitchen/recommendations")
    assert res.status_code == 401
    assert res.json().get("detail") == "Authentication required"


def test_invalid_meal_type_is_rejected():
    res = client.get("/api/kitchen/recommendations", params={"meal_type": "brunch"})
    assert res.status_code == 422
