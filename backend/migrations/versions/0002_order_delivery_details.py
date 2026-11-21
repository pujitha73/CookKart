"""Add delivery details and COD payment method to orders.

Revision ID: 0002_order_delivery_details
Revises: 0001_initial_schema
Create Date: 2026-11-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_order_delivery_details"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("delivery_recipient", sa.String(length=120), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_phone", sa.String(length=20), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_address_line1", sa.String(length=200), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_address_line2", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_city", sa.String(length=100), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_postal_code", sa.String(length=20), server_default=sa.text("''"), nullable=False),
    )
    op.add_column(
        "orders",
        sa.Column("payment_method", sa.String(length=20), server_default=sa.text("'cod'"), nullable=False),
    )


def downgrade() -> None:
    op.drop_column("orders", "payment_method")
    op.drop_column("orders", "delivery_postal_code")
    op.drop_column("orders", "delivery_city")
    op.drop_column("orders", "delivery_address_line2")
    op.drop_column("orders", "delivery_address_line1")
    op.drop_column("orders", "delivery_phone")
    op.drop_column("orders", "delivery_recipient")
