import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ProductIngredientMapping(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "product_ingredient_mappings"
    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient_mapping"),
        Index("ix_product_ingredient_mappings_product_id", "product_id"),
        Index("ix_product_ingredient_mappings_ingredient_id", "ingredient_id"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="CASCADE"),
        nullable=False,
    )
    match_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100, server_default="100")
    substitution_note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    product: Mapped["Product"] = relationship(back_populates="ingredient_mappings")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="product_mappings")
