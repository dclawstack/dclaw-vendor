"""Authentication (Logto JWT, V8.1).

Disabled by default so dev/CI run open. When ``AUTH_ENABLED=true`` and the Logto
vars are configured, ``require_user`` validates the incoming Bearer JWT against
Logto's JWKS (RS256) and rejects missing/invalid tokens with 401. The JWKS is
fetched lazily and cached per signing-key id.

``current_user`` is the non-enforcing variant: it returns the authenticated user
when a valid token is present, otherwise an anonymous dev user — handy for routes
that adapt to auth without requiring it.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import jwt
from fastapi import Depends, HTTPException, Request
from jwt import PyJWKClient

from app.core.config import settings


@dataclass
class AuthUser:
    sub: str
    email: str | None = None
    anonymous: bool = False


ANON = AuthUser(sub="dev", email=None, anonymous=True)

_jwk_client: PyJWKClient | None = None


def _jwks_url() -> str:
    return f"{settings.logto_endpoint.rstrip('/')}/oidc/jwks"


def _client() -> PyJWKClient:
    global _jwk_client
    if _jwk_client is None:
        _jwk_client = PyJWKClient(_jwks_url())
    return _jwk_client


def _bearer(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return None


def _decode(token: str) -> AuthUser:
    signing_key = _client().get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.logto_audience or None,
        issuer=f"{settings.logto_endpoint.rstrip('/')}/oidc",
        options={"verify_aud": bool(settings.logto_audience)},
    )
    return AuthUser(sub=claims.get("sub", "unknown"), email=claims.get("email"))


async def require_user(request: Request) -> AuthUser:
    """Enforce auth on a protected route (no-op when AUTH_ENABLED is false)."""
    if not settings.auth_enabled:
        return ANON
    token = _bearer(request)
    if not token:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        return _decode(token)
    except (jwt.PyJWTError, httpx.HTTPError, Exception) as e:  # noqa: BLE001
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}") from e


async def current_user(request: Request) -> AuthUser:
    """Non-enforcing: returns the user if authenticated, else the anonymous user."""
    if not settings.auth_enabled:
        return ANON
    token = _bearer(request)
    if not token:
        return ANON
    try:
        return _decode(token)
    except Exception:  # noqa: BLE001
        return ANON


def auth_config() -> dict:
    return {
        "enabled": settings.auth_enabled,
        "endpoint": settings.logto_endpoint or None,
        "app_id": settings.logto_app_id or None,
        "audience": settings.logto_audience or None,
    }
