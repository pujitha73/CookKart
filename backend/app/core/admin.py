"""Server-side administrator authorization dependency.

Administrator rights are resolved from the database on every request. The
Supabase access token only establishes *identity*; neither frontend input,
user metadata, nor JWT claims can grant administrator access.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import AuthenticatedUser, CurrentUser
from app.database.session import get_db
from app.models.profile import Profile


def _forbidden() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Administrator access required",
    )


def get_current_admin(
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> AuthenticatedUser:
    """Require an authenticated user whose profile is flagged as an admin.

    A missing profile, a non-admin profile, or a deleted account are all denied
    with 403. The lookup uses the backend's privileged connection, never a
    client-supplied role.
    """
    is_admin = db.execute(
        select(Profile.is_admin).where(Profile.id == current_user.id)
    ).scalar_one_or_none()
    if is_admin is not True:
        raise _forbidden()
    return current_user


CurrentAdmin = Annotated[AuthenticatedUser, Depends(get_current_admin)]
