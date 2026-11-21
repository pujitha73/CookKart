from collections import Counter

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.main import app
from app.database.session import SessionLocal
from app.models.recipe import Ingredient, Recipe, RecipeCollection, RecipeIngredient
from app.models.mapping import ProductIngredientMapping
from seed_recipe_catalogue import main as seed_recipe_catalogue

client = TestClient(app)

MEAL_TYPES = ("breakfast-tiffin", "lunch-dinner", "snack")
COLLECTIONS = ("south-indian", "north-indian", "chinese", "italian", "quick-meals")


def test_list_collections():
    res = client.get("/api/recipes/collections")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 5
    assert {item["slug"] for item in data} == set(COLLECTIONS)
    assert all(item["recipe_count"] == 5 for item in data)


def test_collection_distribution():
    """Each collection has exactly 2/2/1 recipes across the meal types."""
    for collection in COLLECTIONS:
        res = client.get("/api/recipes", params={"collection": collection, "page_size": 50})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 5
        counts = Counter(item["meal_type"] for item in data["items"])
        assert counts == Counter({"breakfast-tiffin": 2, "lunch-dinner": 2, "snack": 1})


def test_list_recipes_default_pagination():
    res = client.get("/api/recipes")
    assert res.status_code == 200
    data = res.json()
    assert {"items", "total", "page", "page_size", "pages"} <= set(data.keys())
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["page_size"] == 12
    assert data["pages"] == 3
    assert len(data["items"]) == 12


def test_recipe_search_treats_like_wildcards_literally():
    # A bare '_' must not match every single-character name fragment.
    res = client.get("/api/recipes", params={"search": "_", "page_size": 50})
    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_recipe_pagination():
    first_page = client.get("/api/recipes", params={"page": 1, "page_size": 5}).json()
    second_page = client.get("/api/recipes", params={"page": 2, "page_size": 5}).json()
    assert second_page["page"] == 2
    assert second_page["page_size"] == 5
    assert second_page["pages"] == 5
    assert len(second_page["items"]) == 5
    assert {item["slug"] for item in first_page["items"]}.isdisjoint(
        item["slug"] for item in second_page["items"]
    )


def test_filter_by_meal_type():
    expected = {"breakfast-tiffin": 10, "lunch-dinner": 10, "snack": 5}
    for meal_type in MEAL_TYPES:
        res = client.get("/api/recipes", params={"meal_type": meal_type, "page_size": 50})
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == expected[meal_type]
        assert all(item["meal_type"] == meal_type for item in data["items"])


def test_combined_collection_and_meal_type_filters():
    res = client.get(
        "/api/recipes",
        params={"collection": "south-indian", "meal_type": "breakfast-tiffin"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert {item["slug"] for item in data["items"]} == {"idli", "masala-dosa"}


def test_search_by_recipe_name():
    res = client.get("/api/recipes", params={"search": "dosa"})
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["slug"] == "masala-dosa"


def test_search_with_filter_returns_empty():
    res = client.get(
        "/api/recipes",
        params={"search": "definitely-not-a-recipe-name", "collection": "italian"},
    )
    assert res.status_code == 200
    assert res.json()["items"] == []


def test_recipe_detail_serialization():
    res = client.get("/api/recipes/idli")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Idli"
    assert data["slug"] == "idli"
    assert data["collection"]["slug"] == "south-indian"
    assert data["meal_type"] == "breakfast-tiffin"
    assert data["prep_time_minutes"] == 25
    assert data["cook_time_minutes"] == 15
    assert data["serving_size"] == 4
    assert data["image_url"].startswith("https://upload.wikimedia.org/")
    assert data["youtube_video_id"] == "Ayo80PIb-Qg"
    assert data["youtube_url"].endswith("Ayo80PIb-Qg")

    assert isinstance(data["instructions"], list)
    assert len(data["instructions"]) == 6
    assert all(isinstance(step, str) and step for step in data["instructions"])

    ingredients = data["ingredients"]
    assert len(ingredients) == 4
    assert [item["name"] for item in ingredients] == [
        "Idli Rice",
        "Urad Dal",
        "Fenugreek Seeds",
        "Salt",
    ]
    assert [item["display_order"] for item in ingredients] == [0, 1, 2, 3]
    assert ingredients[0]["quantity"] == "2"
    assert ingredients[0]["unit"] == "cups"
    assert ingredients[2]["quantity"] == "0.5"
    assert ingredients[3]["quantity"] is None
    assert ingredients[3]["unit"] == "to taste"


def test_all_recipe_details_have_complete_data():
    listed = client.get("/api/recipes", params={"page_size": 50}).json()["items"]
    assert len(listed) == 25
    for item in listed:
        detail = client.get(f"/api/recipes/{item['slug']}")
        assert detail.status_code == 200
        data = detail.json()
        assert data["description"]
        assert data["image_url"]
        assert data["youtube_video_id"] and len(data["youtube_video_id"]) == 11
        assert len(data["instructions"]) >= 5
        assert len(data["ingredients"]) >= 4
        assert [link["display_order"] for link in data["ingredients"]] == list(
            range(len(data["ingredients"]))
        )


def test_recipe_detail_not_found():
    res = client.get("/api/recipes/this-recipe-does-not-exist-12345")
    assert res.status_code == 404
    assert res.json().get("detail") == "Recipe not found"


def test_invalid_pagination_parameters():
    assert client.get("/api/recipes", params={"page": 0}).status_code == 422
    assert client.get("/api/recipes", params={"page_size": 51}).status_code == 422
    assert client.get("/api/recipes", params={"page": "abc"}).status_code == 422


def test_invalid_meal_type_parameter():
    res = client.get("/api/recipes", params={"meal_type": "brunch"})
    assert res.status_code == 422


def test_seed_is_idempotent_and_prevents_duplicates():
    def snapshot():
        with SessionLocal() as db:
            return {
                "collections": db.execute(select(func.count()).select_from(RecipeCollection)).scalar_one(),
                "recipes": db.execute(select(func.count()).select_from(Recipe)).scalar_one(),
                "ingredients": db.execute(select(func.count()).select_from(Ingredient)).scalar_one(),
                "links": db.execute(select(func.count()).select_from(RecipeIngredient)).scalar_one(),
                "mappings": db.execute(select(func.count()).select_from(ProductIngredientMapping)).scalar_one(),
            }

    before = snapshot()
    assert before["collections"] == 5
    assert before["recipes"] == 25
    assert 60 <= before["ingredients"] <= 70

    assert seed_recipe_catalogue() == 0
    assert seed_recipe_catalogue() == 0
    assert snapshot() == before
