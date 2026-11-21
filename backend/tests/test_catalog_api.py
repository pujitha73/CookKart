from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_list_categories():
    res = client.get("/api/catalog/categories")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)


def test_list_products_default_pagination():
    res = client.get("/api/catalog/products")
    assert res.status_code == 200
    data = res.json()
    assert {"items", "total", "page", "page_size", "pages"} <= set(data.keys())
    assert data["page"] == 1
    assert data["page_size"] == 12
    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)


def test_list_products_with_search_and_pagination_params():
    res = client.get("/api/catalog/products", params={"search": "nonexistent-product-name-xyz", "page": 1, "page_size": 5})
    assert res.status_code == 200
    data = res.json()
    assert data["page"] == 1
    assert data["page_size"] == 5
    assert isinstance(data["items"], list)


def test_list_products_search_treats_like_wildcards_literally():
    # A bare '%' must not be interpreted as a match-everything wildcard.
    res = client.get("/api/catalog/products", params={"search": "%", "page_size": 50})
    assert res.status_code == 200
    assert res.json()["total"] == 0


def test_list_products_validation_error_for_invalid_page():
    res = client.get("/api/catalog/products", params={"page": 0})
    assert res.status_code == 422


def test_product_detail_not_found():
    res = client.get("/api/catalog/products/this-product-slug-does-not-exist-12345")
    assert res.status_code == 404
    assert res.json().get("detail") == "Product not found"
