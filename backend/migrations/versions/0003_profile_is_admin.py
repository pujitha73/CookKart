"""Add a database-backed administrator flag to user profiles.

The flag defaults to false for every existing and new profile. No account is
promoted automatically. Customers are explicitly denied INSERT/UPDATE on the
new column so they cannot promote themselves through PostgREST/Supabase; only
the privileged backend connection can change it (see README).

Revision ID: 0003_profile_is_admin
Revises: 0002_order_delivery_details
Create Date: 2026-11-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_profile_is_admin"
down_revision = "0002_order_delivery_details"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "profiles",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    # RLS already limits customers to their own profile row, but Supabase grants
    # anon/authenticated broad table-level INSERT/UPDATE privileges. That would let
    # a customer PATCH {"is_admin": true} on their own row. Replace the table-level
    # grants with column-scoped grants that deliberately exclude is_admin.
    op.execute("REVOKE INSERT, UPDATE ON TABLE public.profiles FROM anon, authenticated")
    op.execute("GRANT INSERT (id, display_name, avatar_url) ON TABLE public.profiles TO authenticated")
    op.execute("GRANT UPDATE (display_name, avatar_url) ON TABLE public.profiles TO authenticated")


def downgrade() -> None:
    op.execute("REVOKE INSERT (id, display_name, avatar_url) ON TABLE public.profiles FROM authenticated")
    op.execute("REVOKE UPDATE (display_name, avatar_url) ON TABLE public.profiles FROM authenticated")
    op.execute("GRANT INSERT, UPDATE ON TABLE public.profiles TO anon, authenticated")
    op.drop_column("profiles", "is_admin")
