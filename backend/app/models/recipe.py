import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class RecipeCollection(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recipe_collections"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, unique=True, index=True)
    cuisine_label: Mapped[str | None] = mapped_column(String(120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="collection")


class Recipe(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recipes"
    __table_args__ = (
        Index("ix_recipes_collection_id", "collection_id"),
        Index("ix_recipes_meal_type", "meal_type"),
    )

    collection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipe_collections.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False, unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    meal_type: Mapped[str] = mapped_column(String(30), nullable=False)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cook_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[str | None] = mapped_column(String(30), nullable=True)
    serving_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    youtube_video_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    youtube_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    collection: Mapped["RecipeCollection"] = relationship(back_populates="recipes")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe", cascade="all, delete-orphan"
    )
    saved_by: Mapped[list["SavedRecipe"]] = relationship(back_populates="recipe")


class Ingredient(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "ingredients"

    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    normalized_name: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)

    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(back_populates="ingredient")
    product_mappings: Mapped[list["ProductIngredientMapping"]] = relationship(back_populates="ingredient")
    pantry_entries: Mapped[list["UserPantry"]] = relationship(back_populates="ingredient")


class RecipeIngredient(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "recipe_ingredients"
    __table_args__ = (
        UniqueConstraint("recipe_id", "ingredient_id", "display_order", name="uq_recipe_ingredient_order"),
        Index("ix_recipe_ingredients_recipe_id", "recipe_id"),
        Index("ix_recipe_ingredients_ingredient_id", "ingredient_id"),
    )

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
    )
    ingredient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ingredients.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    preparation_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_ingredients")
