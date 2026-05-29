"""Phase 8 — V8.1 Auth (Logto JWT), feature-flagged."""

import pytest

from app.core import auth as auth_mod
from app.core.config import settings


@pytest.fixture
def auth_on():
    settings.auth_enabled = True
    settings.logto_endpoint = "https://example.logto.app"
    auth_mod._jwk_client = None
    yield
    settings.auth_enabled = False
    auth_mod._jwk_client = None


@pytest.mark.asyncio
async def test_config_reports_disabled_by_default(client):
    r = await client.get("/api/v1/auth/config")
    assert r.status_code == 200
    assert r.json()["enabled"] is False


@pytest.mark.asyncio
async def test_me_anonymous_when_disabled(client):
    r = await client.get("/api/v1/auth/me")
    assert r.json()["anonymous"] is True


@pytest.mark.asyncio
async def test_protected_open_when_disabled(client):
    # AUTH_ENABLED is false by default -> vendors route is open
    r = await client.get("/api/v1/vendors")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_protected_requires_token_when_enabled(client, auth_on):
    r = await client.get("/api/v1/vendors")
    assert r.status_code == 401
    assert "Missing bearer token" in r.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_token_rejected_when_enabled(client, auth_on):
    r = await client.get(
        "/api/v1/vendors", headers={"Authorization": "Bearer not.a.jwt"}
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_config_reports_enabled(client, auth_on):
    r = await client.get("/api/v1/auth/config")
    assert r.json()["enabled"] is True
    assert r.json()["endpoint"] == "https://example.logto.app"
