from sqlalchemy import Column, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


# Supabase Auth owns auth.users. Application models reference it with a
# foreign key, so SQLAlchemy needs a metadata-only definition for mapper
# configuration. This table is never created or modified by the application.
auth_users_table = Table(
    "users",
    Base.metadata,
    Column("id", UUID(as_uuid=True), primary_key=True),
    schema="auth",
)
