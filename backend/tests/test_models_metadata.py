from sqlalchemy import UniqueConstraint

from app.database.base import Base
import app.models  # noqa: F401


def test_all_required_tables_present():
    tables = set(Base.metadata.tables.keys())
    required = {
        "profiles",
        "product_categories",
        "products",
        "recipe_collections",
        "recipes",
        "ingredients",
        "recipe_ingredients",
        "product_ingredient_mappings",
        "user_pantry",
        "saved_recipes",
        "shopping_carts",
        "cart_items",
        "orders",
        "order_items",
        "wishlist",
    }
    assert required.issubset(tables)


def test_user_owned_tables_have_user_id_column():
    user_owned = [
        "profiles",  # id references auth.users
        "user_pantry",
        "saved_recipes",
        "shopping_carts",
        "orders",
        "wishlist",
    ]
    for name in ["user_pantry", "saved_recipes", "shopping_carts", "orders", "wishlist"]:
        cols = Base.metadata.tables[name].c
        assert "user_id" in cols
    assert "id" in Base.metadata.tables["profiles"].c


def _has_unique(table_name: str, columns: set[str], name: str | None = None) -> bool:
    table = Base.metadata.tables[table_name]
    for c in table.constraints:
        if isinstance(c, UniqueConstraint):
            if name and c.name == name:
                return True
            if {col.name for col in c.columns} == columns:
                return True
    for idx in table.indexes:
        if idx.unique and {col.name for col in idx.columns} == columns:
            return True
    return False


def test_key_unique_constraints_defined():
    assert _has_unique("product_categories", {"slug"})
    assert _has_unique("products", {"slug"})
    assert _has_unique("recipe_collections", {"slug"})
    assert _has_unique("recipes", {"slug"})
    assert _has_unique("ingredients", {"name"})
    assert _has_unique("recipe_ingredients", {"recipe_id", "ingredient_id", "display_order"})
    assert _has_unique("product_ingredient_mappings", {"product_id", "ingredient_id"})
    assert _has_unique("user_pantry", {"user_id", "ingredient_id"})
    assert _has_unique("saved_recipes", {"user_id", "recipe_id"})
    assert _has_unique("cart_items", {"cart_id", "product_id"})
    assert _has_unique("wishlist", {"user_id", "product_id"})


def test_foreign_keys_present_for_core_relationships():
    recipes = Base.metadata.tables["recipes"]
    fk_targets = {fk.target_fullname for fk in recipes.foreign_keys}
    assert "recipe_collections.id" in fk_targets

    order_items = Base.metadata.tables["order_items"]
    oi_fks = {fk.target_fullname for fk in order_items.foreign_keys}
    assert "orders.id" in oi_fks
    assert "products.id" in oi_fks

    cart_items = Base.metadata.tables["cart_items"]
    ci_fks = {fk.target_fullname for fk in cart_items.foreign_keys}
    assert "shopping_carts.id" in ci_fks
    assert "products.id" in ci_fks


def test_order_items_preserve_historical_snapshots():
    cols = Base.metadata.tables["order_items"].c
    assert "product_name_snapshot" in cols
    assert "unit_price_snapshot" in cols
    assert "line_total_snapshot" in cols
    assert cols["product_id"].nullable is True


def test_orders_store_cod_delivery_details():
    cols = Base.metadata.tables["orders"].c
    for name in (
        "delivery_recipient",
        "delivery_phone",
        "delivery_address_line1",
        "delivery_address_line2",
        "delivery_city",
        "delivery_postal_code",
        "payment_method",
    ):
        assert name in cols
    assert cols["delivery_address_line2"].nullable is True
    assert cols["payment_method"].nullable is False


def test_profiles_have_database_backed_admin_flag():
    cols = Base.metadata.tables["profiles"].c
    assert "is_admin" in cols
    assert cols["is_admin"].nullable is False
    assert cols["is_admin"].default.arg is False
