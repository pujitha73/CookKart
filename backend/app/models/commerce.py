import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class ShoppingCart(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "shopping_carts"
    __table_args__ = (
        Index("ix_shopping_carts_user_id", "user_id"),
        Index(
            "uq_shopping_carts_active_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'active'"),
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", server_default="active")

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_item_cart_product"),
        Index("ix_cart_items_cart_id", "cart_id"),
        Index("ix_cart_items_product_id", "product_id"),
    )

    cart_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("shopping_carts.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    unit_price_snapshot: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    cart: Mapped["ShoppingCart"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="cart_items")


class Order(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_user_id", "user_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="placed", server_default="placed")
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=0, server_default="0")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR", server_default="INR")
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    delivery_recipient: Mapped[str] = mapped_column(String(120), nullable=False, default="", server_default="")
    delivery_phone: Mapped[str] = mapped_column(String(20), nullable=False, default="", server_default="")
    delivery_address_line1: Mapped[str] = mapped_column(String(200), nullable=False, default="", server_default="")
    delivery_address_line2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    delivery_city: Mapped[str] = mapped_column(String(100), nullable=False, default="", server_default="")
    delivery_postal_code: Mapped[str] = mapped_column(String(20), nullable=False, default="", server_default="")
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False, default="cod", server_default="cod")

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "order_items"
    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_product_id", "product_id"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    line_total_snapshot: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product | None"] = relationship(back_populates="order_items")


class Wishlist(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "wishlist"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
        Index("ix_wishlist_user_id", "user_id"),
        Index("ix_wishlist_product_id", "product_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="wishlist_items")
