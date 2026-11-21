import asyncio
import uuid

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core import auth as auth_module
from app.core.auth import AuthenticatedUser, get_authenticated_user
from app.database.session import SessionLocal
from app.main import app
from app.models.recipe import Ingredient, Recipe

client = TestClient(app)


@pytest.fixture(scope="module")
def kitchen_users():
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


def use_user(user_id):
    app.dependency_overrides[get_authenticated_user] = lambda uid=user_id: AuthenticatedUser(
        id=uid, email="phase6-test@example.test"
    )


@pytest.fixture(autouse=True)
def clean_kitchen_state(kitchen_users):
    db = SessionLocal()
    try:
        for user_id in kitchen_users:
            db.execute(text("DELETE FROM saved_recipes WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
        db.commit()
    finally:
        db.close()

    use_user(kitchen_users[0])
    yield
    app.dependency_overrides.pop(get_authenticated_user, None)

    db = SessionLocal()
    try:
        for user_id in kitchen_users:
            db.execute(text("DELETE FROM saved_recipes WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM user_pantry WHERE user_id = :uid"), {"uid": user_id})
        db.commit()
    finally:
        db.close()


def first_ingredient_id():
    with SessionLocal() as db:
        from sqlalchemy import select

        return db.execute(select(Ingredient.id).order_by(Ingredient.name.asc())).scalars().first()


def first_recipe():
    with SessionLocal() as db:
        from sqlalchemy import select

        return db.execute(select(Recipe).order_by(Recipe.name.asc())).scalars().first()


def test_missing_bearer_token_is_rejected():
    app.dependency_overrides.pop(get_authenticated_user, None)
    res = client.get("/api/kitchen/pantry")
    assert res.status_code == 401
    assert res.json().get("detail") == "Authentication required"


def test_invalid_bearer_token_is_rejected(monkeypatch):
    app.dependency_overrides.pop(get_authenticated_user, None)

    async def reject(_token: str):
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token")

    monkeypatch.setattr(auth_module, "fetch_supabase_user", reject)
    res = client.get("/api/kitchen/pantry", headers={"Authorization": "Bearer invalid-token"})
    assert res.status_code == 401
    assert "expired" in res.json().get("detail", "").lower()


def test_valid_access_token_resolves_authenticated_user(kitchen_users, monkeypatch):
    async def valid_user(token: str):
        assert token == "valid-token"
        return {"id": str(kitchen_users[0]), "email": "phase6-test@example.test"}

    monkeypatch.setattr(auth_module, "fetch_supabase_user", valid_user)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valid-token")
    user = asyncio.run(get_authenticated_user(credentials))
    assert user.id == kitchen_users[0]
    assert user.email == "phase6-test@example.test"


def test_ingredient_catalogue_requires_auth_but_returns_catalogue_for_user(kitchen_users):
    res = client.get("/api/kitchen/ingredients")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 60
    assert {"id", "name", "normalized_name"} <= set(data[0])


def test_pantry_crud_and_duplicate_addition(kitchen_users):
    ingredient_id = first_ingredient_id()
    payload = {
        "ingredient_id": str(ingredient_id),
        "quantity": "2.500",
        "unit": "cups",
        "is_available": True,
    }

    created = client.post("/api/kitchen/pantry", json=payload)
    assert created.status_code == 201
    entry = created.json()
    assert entry["ingredient"]["id"] == str(ingredient_id)
    assert entry["quantity"] == "2.5"
    assert entry["unit"] == "cups"
    assert entry["is_available"] is True

    duplicate = client.post("/api/kitchen/pantry", json=payload)
    assert duplicate.status_code == 409
    assert "already" in duplicate.json().get("detail", "").lower()

    listed = client.get("/api/kitchen/pantry")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [entry["id"]]

    updated = client.patch(
        f"/api/kitchen/pantry/{entry['id']}",
        json={"quantity": "0", "unit": "tbsp", "is_available": False},
    )
    assert updated.status_code == 200
    updated_json = updated.json()
    assert updated_json["quantity"] == "0"
    assert updated_json["unit"] == "tbsp"
    assert updated_json["is_available"] is False

    deleted = client.delete(f"/api/kitchen/pantry/{entry['id']}")
    assert deleted.status_code == 204
    assert client.get("/api/kitchen/pantry").json() == []


def test_pantry_validation_and_nonexistent_ingredient():
    missing = client.post("/api/kitchen/pantry", json={"ingredient_id": str(uuid.uuid4())})
    assert missing.status_code == 404
    assert missing.json().get("detail") == "Ingredient not found"

    negative = client.post(
        "/api/kitchen/pantry",
        json={"ingredient_id": str(first_ingredient_id()), "quantity": "-1"},
    )
    assert negative.status_code == 422

    entry_id = client.post(
        "/api/kitchen/pantry", json={"ingredient_id": str(first_ingredient_id())}
    ).json()["id"]
    empty_update = client.patch(f"/api/kitchen/pantry/{entry_id}", json={})
    assert empty_update.status_code == 422


def test_pantry_isolation_between_users(kitchen_users):
    use_user(kitchen_users[0])
    entry = client.post(
        "/api/kitchen/pantry", json={"ingredient_id": str(first_ingredient_id())}
    ).json()

    use_user(kitchen_users[1])
    assert client.get("/api/kitchen/pantry").json() == []
    assert client.patch(f"/api/kitchen/pantry/{entry['id']}", json={"unit": "g"}).status_code == 404
    assert client.delete(f"/api/kitchen/pantry/{entry['id']}").status_code == 404


def test_saved_recipes_crud_duplicate_and_isolation(kitchen_users):
    recipe = first_recipe()

    created = client.post("/api/kitchen/saved-recipes", json={"recipe_id": str(recipe.id)})
    assert created.status_code == 201
    saved = created.json()
    assert saved["recipe"]["id"] == str(recipe.id)
    assert saved["recipe"]["slug"] == recipe.slug
    assert saved["recipe"]["collection"]["slug"]

    duplicate = client.post("/api/kitchen/saved-recipes", json={"recipe_id": str(recipe.id)})
    assert duplicate.status_code == 409
    assert "already" in duplicate.json().get("detail", "").lower()

    listed = client.get("/api/kitchen/saved-recipes")
    assert listed.status_code == 200
    assert [item["recipe"]["id"] for item in listed.json()] == [str(recipe.id)]

    use_user(kitchen_users[1])
    assert client.get("/api/kitchen/saved-recipes").json() == []
    assert client.delete(f"/api/kitchen/saved-recipes/{recipe.id}").status_code == 404

    use_user(kitchen_users[0])
    deleted = client.delete(f"/api/kitchen/saved-recipes/{recipe.id}")
    assert deleted.status_code == 204
    assert client.get("/api/kitchen/saved-recipes").json() == []


def test_malformed_identifiers_return_validation_errors():
    # Invalid UUID path parameters must be rejected by validation, never
    # passed to the database where they could surface as a 500.
    assert client.patch("/api/kitchen/pantry/not-a-uuid", json={"unit": "g"}).status_code == 422
    assert client.delete("/api/kitchen/pantry/not-a-uuid").status_code == 422
    assert client.delete("/api/kitchen/saved-recipes/not-a-uuid").status_code == 422


def test_saved_recipe_nonexistent_and_invalid_payload():
    missing = client.post("/api/kitchen/saved-recipes", json={"recipe_id": str(uuid.uuid4())})
    assert missing.status_code == 404
    assert missing.json().get("detail") == "Recipe not found"

    invalid = client.post("/api/kitchen/saved-recipes", json={"slug": "idli"})
    assert invalid.status_code == 422
