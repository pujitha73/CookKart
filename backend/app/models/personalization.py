import uuid
from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class UserPantry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "user_pantry"
    __table_args__ = (
        UniqueConstraint("user_id", "ingredient_id", name="uq_user_pantry_user_ingredient"),
        Index("ix_user_pantry_user_id", "user_id"),
        Index("ix_user_pantry_ingredient_id", "ingredient_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    ingredient: Mapped["Ingredient"] = relationship(back_populates="pantry_entries")


class SavedRecipe(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "saved_recipes"
    __table_args__ = (
        UniqueConstraint("user_id", "recipe_id", name="uq_saved_recipe_user_recipe"),
        Index("ix_saved_recipes_user_id", "user_id"),
        Index("ix_saved_recipes_recipe_id", "recipe_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )

    recipe: Mapped["Recipe"] = relationship(back_populates="saved_by")
