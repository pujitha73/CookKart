"""Repair two product image URLs that became permanently unavailable.

The original Unsplash photos for Tomatoes and Iodized Salt now return HTTP 404.
Both are replaced with stable Wikimedia Commons thumbnails depicting the same
actual product, matching the Wikimedia images already used by other catalogue
items. No prices, names, descriptions or other product data are changed.

Revision ID: 0004_repair_product_images
Revises: 0003_profile_is_admin
Create Date: 2026-11-17
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0004_repair_product_images"
down_revision = "0003_profile_is_admin"
branch_labels = None
depends_on = None

_TOMATOES_OLD = "https://images.unsplash.com/photo-1546470427-227c7369a9b3?auto=format&fit=crop&w=800&q=80"
_TOMATOES_NEW = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/"
    "Bright_red_tomato_and_cross_section02.jpg/960px-Bright_red_tomato_and_cross_section02.jpg"
)
_SALT_OLD = "https://images.unsplash.com/photo-1518110925495-5fe2fda28289?auto=format&fit=crop&w=800&q=80"
_SALT_NEW = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/EdibleSalt.jpg/960px-EdibleSalt.jpg"


def upgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE products SET image_url = :url "
            "WHERE slug = 'tomatoes-1kg' AND image_url = :old"
        ).bindparams(url=_TOMATOES_NEW, old=_TOMATOES_OLD)
    )
    op.execute(
        sa.text(
            "UPDATE products SET image_url = :url "
            "WHERE slug = 'iodized-salt-1kg' AND image_url = :old"
        ).bindparams(url=_SALT_NEW, old=_SALT_OLD)
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            "UPDATE products SET image_url = :url "
            "WHERE slug = 'tomatoes-1kg' AND image_url = :new"
        ).bindparams(url=_TOMATOES_OLD, new=_TOMATOES_NEW)
    )
    op.execute(
        sa.text(
            "UPDATE products SET image_url = :url "
            "WHERE slug = 'iodized-salt-1kg' AND image_url = :new"
        ).bindparams(url=_SALT_OLD, new=_SALT_NEW)
    )
