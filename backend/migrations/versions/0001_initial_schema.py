"""Initial CookKart schema, indexes, constraints, and RLS policies.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Identity
    op.create_table(
        "profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("avatar_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # Catalogue
    op.create_table(
        "product_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_product_categories_name"),
        sa.UniqueConstraint("slug", name="uq_product_categories_slug"),
    )
    op.create_index("ix_product_categories_slug", "product_categories", ["slug"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("product_categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("size", sa.String(length=50), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("slug", name="uq_products_slug"),
    )
    op.create_index("ix_products_category_id", "products", ["category_id"], unique=False)
    op.create_index("ix_products_name", "products", ["name"], unique=False)
    op.create_index("ix_products_slug", "products", ["slug"], unique=False)

    # Recipes
    op.create_table(
        "recipe_collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=140), nullable=False),
        sa.Column("cuisine_label", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_recipe_collections_name"),
        sa.UniqueConstraint("slug", name="uq_recipe_collections_slug"),
    )
    op.create_index("ix_recipe_collections_slug", "recipe_collections", ["slug"], unique=False)

    op.create_table(
        "recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("collection_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recipe_collections.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("meal_type", sa.String(length=30), nullable=False),
        sa.Column("prep_time_minutes", sa.Integer(), nullable=True),
        sa.Column("cook_time_minutes", sa.Integer(), nullable=True),
        sa.Column("difficulty", sa.String(length=30), nullable=True),
        sa.Column("serving_size", sa.Integer(), nullable=True),
        sa.Column("image_url", sa.Text(), nullable=True),
        sa.Column("youtube_video_id", sa.String(length=32), nullable=True),
        sa.Column("youtube_url", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("slug", name="uq_recipes_slug"),
    )
    op.create_index("ix_recipes_collection_id", "recipes", ["collection_id"], unique=False)
    op.create_index("ix_recipes_meal_type", "recipes", ["meal_type"], unique=False)
    op.create_index("ix_recipes_slug", "recipes", ["slug"], unique=False)

    op.create_table(
        "ingredients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("normalized_name", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("name", name="uq_ingredients_name"),
        sa.UniqueConstraint("normalized_name", name="uq_ingredients_normalized_name"),
    )
    op.create_index("ix_ingredients_normalized_name", "ingredients", ["normalized_name"], unique=False)

    op.create_table(
        "recipe_ingredients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("preparation_note", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("recipe_id", "ingredient_id", "display_order", name="uq_recipe_ingredient_order"),
    )
    op.create_index("ix_recipe_ingredients_recipe_id", "recipe_ingredients", ["recipe_id"], unique=False)
    op.create_index("ix_recipe_ingredients_ingredient_id", "recipe_ingredients", ["ingredient_id"], unique=False)

    # Mapping
    op.create_table(
        "product_ingredient_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("match_priority", sa.Integer(), server_default=sa.text("100"), nullable=False),
        sa.Column("substitution_note", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient_mapping"),
    )
    op.create_index("ix_product_ingredient_mappings_product_id", "product_ingredient_mappings", ["product_id"], unique=False)
    op.create_index("ix_product_ingredient_mappings_ingredient_id", "product_ingredient_mappings", ["ingredient_id"], unique=False)

    # Personalization (user-owned)
    op.create_table(
        "user_pantry",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ingredient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ingredients.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 3), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.Column("is_available", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "ingredient_id", name="uq_user_pantry_user_ingredient"),
    )
    op.create_index("ix_user_pantry_user_id", "user_pantry", ["user_id"], unique=False)
    op.create_index("ix_user_pantry_ingredient_id", "user_pantry", ["ingredient_id"], unique=False)

    op.create_table(
        "saved_recipes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recipe_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "recipe_id", name="uq_saved_recipe_user_recipe"),
    )
    op.create_index("ix_saved_recipes_user_id", "saved_recipes", ["user_id"], unique=False)
    op.create_index("ix_saved_recipes_recipe_id", "saved_recipes", ["recipe_id"], unique=False)

    # Commerce (user-owned)
    op.create_table(
        "shopping_carts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'active'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_shopping_carts_user_id", "shopping_carts", ["user_id"], unique=False)
    op.create_index(
        "uq_shopping_carts_active_user",
        "shopping_carts",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("status = 'active'"),
    )

    op.create_table(
        "cart_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("cart_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shopping_carts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("unit_price_snapshot", sa.Numeric(10, 2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_item_cart_product"),
    )
    op.create_index("ix_cart_items_cart_id", "cart_items", ["cart_id"], unique=False)
    op.create_index("ix_cart_items_product_id", "cart_items", ["product_id"], unique=False)

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'placed'"), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), server_default=sa.text("0"), nullable=False),
        sa.Column("currency", sa.String(length=10), server_default=sa.text("'INR'"), nullable=False),
        sa.Column("placed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"], unique=False)

    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_name_snapshot", sa.String(length=200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price_snapshot", sa.Numeric(10, 2), nullable=False),
        sa.Column("line_total_snapshot", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"], unique=False)
    op.create_index("ix_order_items_product_id", "order_items", ["product_id"], unique=False)

    op.create_table(
        "wishlist",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )
    op.create_index("ix_wishlist_user_id", "wishlist", ["user_id"], unique=False)
    op.create_index("ix_wishlist_product_id", "wishlist", ["product_id"], unique=False)

    # Row Level Security (RLS) and policies (Supabase/PostgreSQL)
    # NOTE: RLS is enforced for non-owner roles (e.g. anon/authenticated via PostgREST or
    # connections that set request.jwt.claims). Direct SQLAlchemy connections using a
    # privileged DATABASE_URL (postgres/service role) typically bypass RLS unless claims
    # are explicitly set per transaction. Application code must still enforce server-side
    # authorization and ownership checks.
    op.execute("ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE user_pantry ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE saved_recipes ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE shopping_carts ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE orders ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE wishlist ENABLE ROW LEVEL SECURITY;")

    op.execute("ALTER TABLE product_categories ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE products ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE recipe_collections ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE ingredients ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE recipe_ingredients ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE product_ingredient_mappings ENABLE ROW LEVEL SECURITY;")

    # Catalog public read (anon + authenticated)
    for table in [
        "product_categories", "products", "recipe_collections", "recipes",
        "ingredients", "recipe_ingredients", "product_ingredient_mappings",
    ]:
        op.execute(f"""
            CREATE POLICY {table}_select_public ON {table}
            FOR SELECT TO anon, authenticated
            USING (true);
        """)

    # Profiles: owner only
    op.execute("""
        CREATE POLICY profiles_select_own ON profiles
        FOR SELECT TO authenticated
        USING (auth.uid() = id);
    """)
    op.execute("""
        CREATE POLICY profiles_insert_own ON profiles
        FOR INSERT TO authenticated
        WITH CHECK (auth.uid() = id);
    """)
    op.execute("""
        CREATE POLICY profiles_update_own ON profiles
        FOR UPDATE TO authenticated
        USING (auth.uid() = id)
        WITH CHECK (auth.uid() = id);
    """)
    op.execute("""
        CREATE POLICY profiles_delete_own ON profiles
        FOR DELETE TO authenticated
        USING (auth.uid() = id);
    """)

    # User-owned tables (direct user_id ownership)
    def owner_policies(table: str) -> None:
        op.execute(f"""
            CREATE POLICY {table}_select_own ON {table}
            FOR SELECT TO authenticated
            USING (auth.uid() = user_id);
        """)
        op.execute(f"""
            CREATE POLICY {table}_insert_own ON {table}
            FOR INSERT TO authenticated
            WITH CHECK (auth.uid() = user_id);
        """)
        op.execute(f"""
            CREATE POLICY {table}_update_own ON {table}
            FOR UPDATE TO authenticated
            USING (auth.uid() = user_id)
            WITH CHECK (auth.uid() = user_id);
        """)
        op.execute(f"""
            CREATE POLICY {table}_delete_own ON {table}
            FOR DELETE TO authenticated
            USING (auth.uid() = user_id);
        """)

    for t in ["user_pantry", "saved_recipes", "shopping_carts", "orders", "wishlist"]:
        owner_policies(t)

    # Cart items: ownership via parent cart
    op.execute("""
        CREATE POLICY cart_items_select_own ON cart_items
        FOR SELECT TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM shopping_carts c
                WHERE c.id = cart_items.cart_id AND c.user_id = auth.uid()
            )
        );
    """)
    op.execute("""
        CREATE POLICY cart_items_insert_own ON cart_items
        FOR INSERT TO authenticated
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM shopping_carts c
                WHERE c.id = cart_items.cart_id AND c.user_id = auth.uid()
            )
        );
    """)
    op.execute("""
        CREATE POLICY cart_items_update_own ON cart_items
        FOR UPDATE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM shopping_carts c
                WHERE c.id = cart_items.cart_id AND c.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM shopping_carts c
                WHERE c.id = cart_items.cart_id AND c.user_id = auth.uid()
            )
        );
    """)
    op.execute("""
        CREATE POLICY cart_items_delete_own ON cart_items
        FOR DELETE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM shopping_carts c
                WHERE c.id = cart_items.cart_id AND c.user_id = auth.uid()
            )
        );
    """)

    # Order items: ownership via parent order
    op.execute("""
        CREATE POLICY order_items_select_own ON order_items
        FOR SELECT TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_items.order_id AND o.user_id = auth.uid()
            )
        );
    """)
    op.execute("""
        CREATE POLICY order_items_insert_own ON order_items
        FOR INSERT TO authenticated
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_items.order_id AND o.user_id = auth.uid()
            )
        );
    """)
    op.execute("""
        CREATE POLICY order_items_update_own ON order_items
        FOR UPDATE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_items.order_id AND o.user_id = auth.uid()
            )
        )
        WITH CHECK (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_items.order_id AND o.user_id = auth.uid()
            )
        );
    """)
    op.execute("""
        CREATE POLICY order_items_delete_own ON order_items
        FOR DELETE TO authenticated
        USING (
            EXISTS (
                SELECT 1 FROM orders o
                WHERE o.id = order_items.order_id AND o.user_id = auth.uid()
            )
        );
    """)


def downgrade() -> None:
    # Drop policies (best-effort explicit drops)
    for table in [
        "profiles", "user_pantry", "saved_recipes", "shopping_carts", "cart_items",
        "orders", "order_items", "wishlist", "product_categories", "products",
        "recipe_collections", "recipes", "ingredients", "recipe_ingredients",
        "product_ingredient_mappings",
    ]:
        op.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
