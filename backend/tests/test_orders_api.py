import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.auth import AuthenticatedUser, get_authenticated_user
from app.database.session import SessionLocal
from app.main import app
from app.models.catalog import Product, ProductCategory
from app.models.commerce import ShoppingCart
from app.services.orders import OrderServiceError

client = TestClient(app)

VALID_ADDRESS = {
    "recipient_name": "Test Recipient",
    "phone": "9876543210",
    "address_line1": "12 Test Street",
    "address_line2": "Flat 3B",
    "city": "Bengaluru",
    "postal_code": "560001",
}


@pytest.fixture(scope="module")
def orders_fixture():
    user_ids = [uuid.uuid4(), uuid.uuid4()]
    available_product_id = uuid.uuid4()
    second_product_id = uuid.uuid4()
    unavailable_product_id = uuid.uuid4()

    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("INSERT INTO auth.users (id) VALUES (:uid)"), {"uid": user_id})

        category_id = db.execute(select(ProductCategory.id).limit(1)).scalar_one()
        products = [
            (available_product_id, "Phase 9 Test Rice", f"phase9-rice-{available_product_id.hex}", Decimal("120.50"), True),
            (second_product_id, "Phase 9 Test Dal", f"phase9-dal-{second_product_id.hex}", Decimal("80.00"), True),
            (unavailable_product_id, "Phase 9 Unavailable Oil", f"phase9-oil-{unavailable_product_id.hex}", Decimal("50.00"), False),
        ]
        for product_id, name, slug, price, available in products:
            db.execute(
                text(
                    """
                    INSERT INTO products
                        (id, category_id, name, slug, price, unit, size, is_available)
                    VALUES
                        (:id, :category_id, :name, :slug, :price, :unit, :size, :available)
                    """
                ),
                {
                    "id": product_id,
                    "category_id": category_id,
                    "name": name,
                    "slug": slug,
                    "price": price,
                    "unit": "g",
                    "size": "500 g",
                    "available": available,
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
        "second_product_id": second_product_id,
        "unavailable_product_id": unavailable_product_id,
    }

    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("DELETE FROM shopping_carts WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM orders WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM auth.users WHERE id = :uid"), {"uid": user_id})
        for product_id in (available_product_id, second_product_id, unavailable_product_id):
            db.execute(text("DELETE FROM products WHERE id = :pid"), {"pid": product_id})
        db.commit()
    finally:
        db.close()


def use_user(user_id):
    app.dependency_overrides[get_authenticated_user] = lambda uid=user_id: AuthenticatedUser(
        id=uid, email="phase9-orders@example.test"
    )


def clear_state(user_ids):
    db = SessionLocal()
    try:
        for user_id in user_ids:
            db.execute(text("DELETE FROM shopping_carts WHERE user_id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM orders WHERE user_id = :uid"), {"uid": user_id})
        db.commit()
    finally:
        db.close()


def reset_products(fx):
    with SessionLocal() as db:
        for product_id, price, available in (
            (fx["available_product_id"], Decimal("120.50"), True),
            (fx["second_product_id"], Decimal("80.00"), True),
            (fx["unavailable_product_id"], Decimal("50.00"), False),
        ):
            db.execute(
                text(
                    "UPDATE products SET price = :price, is_available = :available "
                    "WHERE id = :pid"
                ),
                {"price": price, "available": available, "pid": product_id},
            )
        db.commit()


@pytest.fixture(autouse=True)
def clean_orders_state(orders_fixture):
    clear_state(orders_fixture["user_ids"])
    reset_products(orders_fixture)
    use_user(orders_fixture["user_ids"][0])
    yield
    app.dependency_overrides.pop(get_authenticated_user, None)
    clear_state(orders_fixture["user_ids"])


def add_to_cart(product_id, quantity=1):
    res = client.post("/api/cart/items", json={"product_id": str(product_id), "quantity": quantity})
    assert res.status_code in (200, 201), res.text
    return res.json()


def set_product(product_id, **fields):
    with SessionLocal() as db:
        for key, value in fields.items():
            db.execute(
                text(f"UPDATE products SET {key} = :value WHERE id = :pid"),
                {"value": value, "pid": product_id},
            )
        db.commit()


def order_count(user_id):
    with SessionLocal() as db:
        return db.execute(
            text("SELECT count(*) FROM orders WHERE user_id = :uid"), {"uid": user_id}
        ).scalar_one()


def place_order(address=None, extra=None):
    body = {"delivery_address": address if address is not None else VALID_ADDRESS}
    if extra:
        body.update(extra)
    return client.post("/api/orders", json=body)


def test_order_requires_authentication(orders_fixture):
    app.dependency_overrides.pop(get_authenticated_user, None)
    res = client.post("/api/orders", json={"delivery_address": VALID_ADDRESS})
    assert res.status_code == 401
    assert order_count(orders_fixture["user_ids"][0]) == 0


def test_empty_cart_checkout_is_rejected():
    res = place_order()
    assert res.status_code == 422
    assert "empty" in res.json()["detail"].lower()


def test_delivery_form_validation():
    # Request-schema validation happens before cart lookup.

    invalid_addresses = [
        {**VALID_ADDRESS, "recipient_name": "A"},
        {**VALID_ADDRESS, "phone": "123"},
        {**VALID_ADDRESS, "address_line1": "x"},
        {**VALID_ADDRESS, "city": ""},
        {**VALID_ADDRESS, "postal_code": "!!"},
    ]
    for address in invalid_addresses:
        res = place_order(address=address)
        assert res.status_code == 422, (address, res.text)


def test_client_cannot_supply_user_totals_or_status(orders_fixture):
    add_to_cart(orders_fixture["available_product_id"], 2)
    res = place_order(extra={"user_id": str(orders_fixture["user_ids"][1]), "total_amount": "1.00", "status": "delivered"})
    assert res.status_code == 422


def test_successful_cod_order_uses_backend_totals_and_snapshots(orders_fixture):
    pid = orders_fixture["available_product_id"]
    add_to_cart(pid, 3)

    res = place_order()
    assert res.status_code == 201, res.text
    order = res.json()

    assert order["status"] == "placed"
    assert order["status_label"] == "Placed"
    assert order["payment_method"] == "cod"
    assert order["currency"] == "INR"
    assert order["order_number"].startswith("CK-")
    assert order["item_count"] == 3
    assert Decimal(order["total_amount"]) == Decimal("361.50")

    assert len(order["items"]) == 1
    item = order["items"][0]
    assert item["product_id"] == str(pid)
    assert item["product_name_snapshot"] == "Phase 9 Test Rice"
    assert Decimal(item["unit_price"]) == Decimal("120.50")
    assert Decimal(item["line_total"]) == Decimal("361.50")
    assert item["quantity"] == 3

    assert order["delivery_address"]["recipient_name"] == "Test Recipient"
    assert order["delivery_address"]["phone"] == "9876543210"
    assert order["delivery_address"]["address_line2"] == "Flat 3B"


def test_order_total_uses_current_database_price(orders_fixture):
    pid = orders_fixture["available_product_id"]
    add_to_cart(pid, 2)
    set_product(pid, price=Decimal("200.00"))

    res = place_order()
    assert res.status_code == 201, res.text
    order = res.json()
    assert Decimal(order["total_amount"]) == Decimal("400.00")
    assert Decimal(order["items"][0]["unit_price"]) == Decimal("200.00")
    assert Decimal(order["items"][0]["line_total"]) == Decimal("400.00")


def test_unavailable_product_is_rejected(orders_fixture):
    pid = orders_fixture["available_product_id"]
    add_to_cart(pid, 1)
    set_product(pid, is_available=False)

    res = place_order()
    assert res.status_code == 409
    assert "available" in res.json()["detail"].lower()
    assert order_count(orders_fixture["user_ids"][0]) == 0

    with SessionLocal() as db:
        cart = db.execute(
            select(ShoppingCart).where(ShoppingCart.user_id == orders_fixture["user_ids"][0])
        ).scalars().one()
        assert cart.status == "active"
        assert len(cart.items) == 1


def test_cart_is_cleared_only_after_success(orders_fixture):
    pid = orders_fixture["available_product_id"]
    add_to_cart(pid, 1)

    res = place_order()
    assert res.status_code == 201, res.text

    with SessionLocal() as db:
        cart = db.execute(
            select(ShoppingCart).where(ShoppingCart.user_id == orders_fixture["user_ids"][0])
        ).scalars().one()
        assert cart.status == "inactive"
        assert len(cart.items) == 0

    second = place_order()
    assert second.status_code == 422
    assert order_count(orders_fixture["user_ids"][0]) == 1


def test_history_and_detail_are_owner_scoped(orders_fixture):
    pid = orders_fixture["available_product_id"]
    add_to_cart(pid, 1)
    created = place_order()
    assert created.status_code == 201, created.text
    order_id = created.json()["id"]

    history = client.get("/api/orders")
    assert history.status_code == 200
    orders = history.json()
    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    assert "items" not in orders[0]

    detail = client.get(f"/api/orders/{order_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == order_id
    assert len(detail.json()["items"]) == 1

    use_user(orders_fixture["user_ids"][1])
    other_history = client.get("/api/orders")
    assert other_history.status_code == 200
    assert other_history.json() == []
    other_detail = client.get(f"/api/orders/{order_id}")
    assert other_detail.status_code == 404


def test_order_status_cannot_be_changed_by_customer(orders_fixture):
    add_to_cart(orders_fixture["available_product_id"], 1)
    created = place_order()
    assert created.status_code == 201, created.text
    order_id = created.json()["id"]

    res = client.patch(f"/api/orders/{order_id}", json={"status": "delivered"})
    assert res.status_code == 405

    with SessionLocal() as db:
        status = db.execute(
            text("SELECT status FROM orders WHERE id = :oid"), {"oid": uuid.UUID(order_id)}
        ).scalar_one()
    assert status == "placed"


def test_order_placement_rolls_back_on_failure(orders_fixture, monkeypatch):
    pid = orders_fixture["available_product_id"]
    add_to_cart(pid, 2)

    def fail_item(*args, **kwargs):
        raise OrderServiceError("simulated failure")

    monkeypatch.setattr("app.services.orders.add_order_item", fail_item)

    res = place_order()
    assert res.status_code == 400
    assert order_count(orders_fixture["user_ids"][0]) == 0

    with SessionLocal() as db:
        cart = db.execute(
            select(ShoppingCart).where(ShoppingCart.user_id == orders_fixture["user_ids"][0])
        ).scalars().one()
        assert cart.status == "active"
        assert len(cart.items) == 1
