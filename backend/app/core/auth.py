"""Reusable Supabase Auth dependency for protected FastAPI routes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer(
    auto_error=False,
    scheme_name="SupabaseAccessToken",
    description="Supabase access token supplied as an Authorization Bearer header.",
)

_UNAUTHENTICATED_HEADERS = {"WWW-Authenticate": "Bearer"}


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    email: str | None = None


def _unauthenticated() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers=_UNAUTHENTICATED_HEADERS,
    )


async def fetch_supabase_user(access_token: str) -> dict:
    """Validate an access token with Supabase Auth and return its user payload.

    The public anon key identifies this app to Supabase; the access token itself
    is the user credential. Supabase validates expiry, signature and issuer, so
    no JWT secret or service-role key is needed here.
    """
    if not settings.supabase_url or not settings.supabase_anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase authentication is not configured",
        )

    url = f"{settings.supabase_url.rstrip('/')}/auth/v1/user"
    headers = {
        "Accept": "application/json",
        "apikey": settings.supabase_anon_key,
        "Authorization": f"Bearer {access_token}",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        ) from exc

    if response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers=_UNAUTHENTICATED_HEADERS,
        )
    if not response.is_success:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is unavailable",
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service returned an invalid response",
        ) from exc

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service returned an invalid response",
        )
    return payload


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    """FastAPI dependency resolving the current Supabase-authenticated user."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthenticated()

    token = credentials.credentials.strip()
    if not token:
        raise _unauthenticated()

    payload = await fetch_supabase_user(token)
    raw_id = payload.get("id")
    try:
        user_id = UUID(str(raw_id))
    except (TypeError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token did not resolve to a valid user",
            headers=_UNAUTHENTICATED_HEADERS,
        ) from exc

    email = payload.get("email")
    return AuthenticatedUser(id=user_id, email=email if isinstance(email, str) else None)


CurrentUser = Annotated[AuthenticatedUser, Depends(get_authenticated_user)]
