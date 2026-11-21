import pytest

from app.database.session import get_db


def test_get_db_raises_clear_error_without_database_url(monkeypatch):
    # Ensure no DATABASE_URL in settings context by reloading session behavior assumption:
    # get_db checks SessionLocal (bound at import). We simulate missing config by calling
    # a small wrapper expectation when SessionLocal is None. In default Phase 3 env without
    # DATABASE_URL, SessionLocal should be None.
    from app.database import session as db_session

    if db_session.SessionLocal is not None:
        pytest.skip("DATABASE_URL configured in environment; cannot assert missing-config behavior")
    with pytest.raises(RuntimeError, match="DATABASE_URL is not configured"):
        next(get_db())
