"""Tests for administrator authentication, authorization, and management APIs."""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.auth import AuthenticatedUser, get_authenticated_user
from app.database.session import SessionLocal
from app.main import app
from app.models.catalog import Product, ProductCategory

client = TestClient(app)

VALID_ADDRESS = {
    "recipient_name": "Admin Test Recipient",
    "phone": "9876543210",
    "address_line1": "12 Test Street",
    "address_line2": "Flat 3B",
    "city": "Bengaluru",
    "postal_code": "560001",
}

ORIGINAL_STATUSES = ("placed", "confirmed", "cancelled")


@pytest.fixture(scope="module")
def admin_fixture():
    admin_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    no_profile_id = uuid.uuid4()
    product_id = uuid.uuid4()
    order_ids = [uuid.uuid4() for _ in ORIGINAL_STATUSES]

    db = SessionLocal()
    try:
        for user_id in (admin_id, customer_id, no_profile_id):
            db.execute(text("INSERT INTO auth.users (id) VALUES (:uid)"), {"uid": user_id})
        db.execute(
            text(
                "INSERT INTO profiles (id, display_name, is_admin) "
                "VALUES (:id, 'Phase 10 Admin', true)"
            ),
            {"id": admin_id},
        )
        db.execute(
            text(
                "INSERT INTO profiles (id, display_name, is_admin) "
                "VALUES (:id, 'Phase 10 Customer', false)"
            ),
            {"id": customer_id},
        )

        category_id = db.execute(select(ProductCategory.id).limit(1)).scalar_one()
        db.execute(
            text(
                """
                INSERT INTO products
                    (id, category_id, name, slug, price, unit, size, is_available)
                VALUES
                    (:id, :category_id, :name, :slug, :price, 'g', '500 g', true)
                """
            ),
            {
                "id": product_id,
                "category_id": category_id,
                "name": f"Phase 10 Admin Test Product {product_id.hex[:6]}",
                "slug": f"phase10-admin-{product_id.hex}",
                "price": Decimal("123.45"),
            },
        )

        for order_id, status in zip(order_ids, ORIGINAL_STATUSES):
            db.execute(
                text(
                    """
                    INSERT INTO orders
                        (id, user_id, status, total_amount, currency, placed_at,
                         delivery_recipient, delivery_phone, delivery_address_line1,
                         delivery_address_line2, delivery_city, delivery_postal_code,
                         payment_method)
                    VALUES
                        (:id, :user_id, :status, 246.90, 'INR', now(),
                         :recipient, :phone, :address1, :address2, :city, :postal, 'cod')
                    """
                ),
                {
                    "id": order_id,
                    "user_id": customer_id,
                    "status": status,
                    "recipient": VALID_ADDRESS["recipient_name"],
                    "phone": VALID_ADDRESS["phone"],
                    "address1": VALID_ADDRESS["address_line1"],
                    "address2": VALID_ADDRESS["address_line2"],
                    "city": VALID_ADDRESS["city"],
                    "postal": VALID_ADDRESS["postal_code"],
                },
            )
            db.execute(
                text(
                    """
                    INSERT INTO order_items
                        (id, order_id, product_id, product_name_snapshot, quantity,
                         unit_price_snapshot, line_total_snapshot)
                    VALUES
                        (:id, :order_id, :product_id, :name, 2, 123.45, 246.90)
                    """
                ),
                {
                    "id": uuid.uuid4(),
                    "order_id": order_id,
                    "product_id": product_id,
                    "name": "Phase 10 Historical Snapshot",
                },
            )
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    yield {
        "admin_id": admin_id,
        "customer_id": customer_id,
        "no_profile_id": no_profile_id,
        "product_id": product_id,
        "order_ids": dict(zip(ORIGINAL_STATUSES, order_ids)),
    }

    db = SessionLocal()
    try:
        for order_id in order_ids:
            db.execute(text("DELETE FROM order_items WHERE order_id = :oid"), {"oid": order_id})
            db.execute(text("DELETE FROM orders WHERE id = :oid"), {"oid": order_id})
        db.execute(text("DELETE FROM products WHERE id = :pid"), {"pid": product_id})
        for user_id in (admin_id, customer_id, no_profile_id):
            db.execute(text("DELETE FROM profiles WHERE id = :uid"), {"uid": user_id})
            db.execute(text("DELETE FROM auth.users WHERE id = :uid"), {"uid": user_id})
        db.commit()
    finally:
        db.close()


def use_user(user_id):
    app.dependency_overrides[get_authenticated_user] = lambda uid=user_id: AuthenticatedUser(
        id=uid, email="phase10-admin@example.test"
    )


def reset_fixture(fx):
    with SessionLocal() as db:
        for status, order_id in fx["order_ids"].items():
            db.execute(
                text("UPDATE orders SET status = :status WHERE id = :oid"),
                {"status": status, "oid": order_id},
            )
        db.execute(
            text("UPDATE products SET is_available = true WHERE id = :pid"),
            {"pid": fx["product_id"]},
        )
        db.commit()


@pytest.fixture(autouse=True)
def clean_admin_state(admin_fixture):
    reset_fixture(admin_fixture)
    use_user(admin_fixture["admin_id"])
    yield
    app.dependency_overrides.pop(get_authenticated_user, None)


def db_status_counts():
    with SessionLocal() as db:
        rows = db.execute(
            text("SELECT status, count(*) FROM orders GROUP BY status")
        ).all()
        return {str(status): int(count) for status, count in rows}


def db_catalogue_counts():
    with SessionLocal() as db:
        return {
            "total_products": int(db.execute(text("SELECT count(*) FROM products")).scalar_one()),
            "available_products": int(
                db.execute(text("SELECT count(*) FROM products WHERE is_available = true")).scalar_one()
            ),
            "unavailable_products": int(
                db.execute(text("SELECT count(*) FROM products WHERE is_available = false")).scalar_one()
            ),
            "total_categories": int(
                db.execute(text("SELECT count(*) FROM product_categories")).scalar_one()
            ),
        }


def admin_endpoints(fx):
    order_id = fx["order_ids"]["placed"]
    return [
        ("GET", "/api/admin/me", None),
        ("GET", "/api/admin/dashboard", None),
        ("GET", "/api/admin/orders", None),
        ("GET", f"/api/admin/orders/{order_id}", None),
        ("PATCH", f"/api/admin/orders/{order_id}/status", {"status": "confirmed"}),
        ("GET", "/api/admin/products", None),
        (
            "PATCH",
            f"/api/admin/products/{fx['product_id']}/availability",
            {"is_available": False},
        ),
    ]


def request(method, path, body=None):
    if body is None:
        return client.request(method, path)
    return client.request(method, path, json=body)


def test_every_admin_endpoint_requires_authentication(admin_fixture):
    app.dependency_overrides.pop(get_authenticated_user, None)
    for method, path, body in admin_endpoints(admin_fixture):
        res = request(method, path, body)
        assert res.status_code == 401, (method, path, res.text)


def test_every_admin_endpoint_denies_customers(admin_fixture):
    use_user(admin_fixture["customer_id"])
    for method, path, body in admin_endpoints(admin_fixture):
        res = request(method, path, body)
        assert res.status_code == 403, (method, path, res.text)
        assert res.json()["detail"] == "Administrator access required"


def test_authenticated_user_without_profile_is_denied(admin_fixture):
    use_user(admin_fixture["no_profile_id"])
    res = client.get("/api/admin/me")
    assert res.status_code == 403


def test_admin_me_reports_database_backed_role(admin_fixture):
    res = client.get("/api/admin/me")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["user_id"] == str(admin_fixture["admin_id"])
    assert body["is_admin"] is True


def test_customer_cannot_set_admin_flag_via_database_privileges():
    """Defence in depth: customers have no DB privilege to change is_admin."""
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                SELECT privilege_type
                FROM information_schema.role_column_grants
                WHERE table_schema = 'public'
                  AND table_name = 'profiles'
                  AND column_name = 'is_admin'
                  AND grantee = 'authenticated'
                """
            )
        ).scalars().all()
    assert "UPDATE" not in rows
    assert "INSERT" not in rows


def test_dashboard_uses_only_real_database_records():
    res = client.get("/api/admin/dashboard")
    assert res.status_code == 200, res.text
    body = res.json()
    counts = db_status_counts()
    catalogue = db_catalogue_counts()

    assert body["total_orders"] == sum(counts.values())
    assert body["awaiting_confirmation"] == counts.get("placed", 0)
    assert body["confirmed_orders"] == counts.get("confirmed", 0)
    assert body["cancelled_orders"] == counts.get("cancelled", 0)
    assert body["catalogue"] == catalogue


def test_order_list_search_and_status_filter(admin_fixture):
    placed_id = admin_fixture["order_ids"]["placed"]
    detail = client.get(f"/api/admin/orders/{placed_id}")
    assert detail.status_code == 200, detail.text
    order_number = detail.json()["order_number"]

    res = client.get("/api/admin/orders", params={"search": order_number[-6:]})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["total"] >= 1
    assert any(item["order_number"] == order_number for item in body["items"])

    empty = client.get("/api/admin/orders", params={"search": "CK-NO-SUCH-ORDER"})
    assert empty.status_code == 200
    assert empty.json()["total"] == 0
    assert empty.json()["items"] == []

    for expected_status in ORIGINAL_STATUSES:
        filtered = client.get("/api/admin/orders", params={"status": expected_status})
        assert filtered.status_code == 200, filtered.text
        filtered_body = filtered.json()
        assert filtered_body["total"] == db_status_counts().get(expected_status, 0)
        assert all(item["status"] == expected_status for item in filtered_body["items"])

    invalid = client.get("/api/admin/orders", params={"status": "delivered"})
    assert invalid.status_code == 422


def test_order_detail_exposes_delivery_items_and_totals(admin_fixture):
    order_id = admin_fixture["order_ids"]["placed"]
    res = client.get(f"/api/admin/orders/{order_id}")
    assert res.status_code == 200, res.text
    body = res.json()

    assert body["id"] == str(order_id)
    assert body["currency"] == "INR"
    assert body["payment_method"] == "cod"
    assert body["delivery_address"]["recipient_name"] == VALID_ADDRESS["recipient_name"]
    assert body["delivery_address"]["address_line2"] == VALID_ADDRESS["address_line2"]
    assert len(body["items"]) == 1
    assert body["items"][0]["product_name_snapshot"] == "Phase 10 Historical Snapshot"
    assert Decimal(body["total_amount"]) == Decimal("246.90")

    missing = client.get(f"/api/admin/orders/{uuid.uuid4()}")
    assert missing.status_code == 404


def test_valid_status_transitions(admin_fixture):
    placed_id = admin_fixture["order_ids"]["placed"]
    confirmed_id = admin_fixture["order_ids"]["confirmed"]

    cases = [
        (placed_id, "confirmed"),
        (placed_id, "cancelled"),
        (confirmed_id, "cancelled"),
    ]
    for order_id, target in cases:
        before = client.get(f"/api/admin/orders/{order_id}").json()
        res = client.patch(
            f"/api/admin/orders/{order_id}/status", json={"status": target}
        )
        assert res.status_code == 200, (target, res.text)
        after = res.json()
        assert after["status"] == target
        # Historical prices, snapshots and totals must never change.
        assert after["total_amount"] == before["total_amount"]
        assert after["items"] == before["items"]

        reset_fixture(admin_fixture)


def test_invalid_status_transitions_are_rejected(admin_fixture):
    cases = [
        (admin_fixture["order_ids"]["placed"], "placed"),
        (admin_fixture["order_ids"]["confirmed"], "placed"),
        (admin_fixture["order_ids"]["cancelled"], "confirmed"),
        (admin_fixture["order_ids"]["cancelled"], "placed"),
    ]
    for order_id, target in cases:
        res = client.patch(
            f"/api/admin/orders/{order_id}/status", json={"status": target}
        )
        assert res.status_code == 409, (target, res.text)

    unknown = client.patch(
        f"/api/admin/orders/{admin_fixture['order_ids']['placed']}/status",
        json={"status": "delivered"},
    )
    assert unknown.status_code == 422

    extra = client.patch(
        f"/api/admin/orders/{admin_fixture['order_ids']['placed']}/status",
        json={"status": "confirmed", "total_amount": "1.00"},
    )
    assert extra.status_code == 422

    missing = client.patch(
        f"/api/admin/orders/{uuid.uuid4()}/status", json={"status": "confirmed"}
    )
    assert missing.status_code == 404


def test_admin_status_change_is_visible_in_customer_history(admin_fixture):
    order_id = admin_fixture["order_ids"]["placed"]
    res = client.patch(
        f"/api/admin/orders/{order_id}/status", json={"status": "confirmed"}
    )
    assert res.status_code == 200, res.text

    use_user(admin_fixture["customer_id"])
    history = client.get("/api/orders")
    assert history.status_code == 200, history.text
    match = [item for item in history.json() if item["id"] == str(order_id)]
    assert len(match) == 1
    assert match[0]["status"] == "confirmed"


def test_product_browse_search_and_availability_toggle(admin_fixture):
    product_id = admin_fixture["product_id"]
    search_term = f"Phase 10 Admin Test Product {product_id.hex[:6]}"

    listed = client.get(
        "/api/admin/products", params={"search": search_term, "availability": "all"}
    )
    assert listed.status_code == 200, listed.text
    items = listed.json()["items"]
    assert any(item["id"] == str(product_id) for item in items)

    disabled = client.patch(
        f"/api/admin/products/{product_id}/availability",
        json={"is_available": False},
    )
    assert disabled.status_code == 200, disabled.text
    assert disabled.json()["is_available"] is False
    assert Decimal(disabled.json()["price"]) == Decimal("123.45")

    with SessionLocal() as db:
        stored = db.execute(
            select(Product).where(Product.id == product_id)
        ).scalar_one()
        assert stored.is_available is False
        assert stored.price == Decimal("123.45")

    unavailable = client.get(
        "/api/admin/products",
        params={"search": search_term, "availability": "unavailable"},
    )
    assert unavailable.status_code == 200
    assert any(item["id"] == str(product_id) for item in unavailable.json()["items"])

    enabled = client.patch(
        f"/api/admin/products/{product_id}/availability",
        json={"is_available": True},
    )
    assert enabled.status_code == 200, enabled.text
    assert enabled.json()["is_available"] is True

    invalid_filter = client.get(
        "/api/admin/products", params={"availability": "in-stock"}
    )
    assert invalid_filter.status_code == 422

    missing = client.patch(
        f"/api/admin/products/{uuid.uuid4()}/availability",
        json={"is_available": False},
    )
    assert missing.status_code == 404
