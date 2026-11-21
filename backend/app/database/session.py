from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True) if settings.database_url else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for database sessions."""
    if SessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in backend/.env to enable database access."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
