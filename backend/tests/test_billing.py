"""Phase 8 — V8.2 Billing (Stripe), mock backend."""

import pytest


@pytest.mark.asyncio
async def test_plans(client):
    r = await client.get("/api/v1/billing/plans")
    assert r.status_code == 200
    plans = r.json()
    ids = {p["id"] for p in plans}
    assert {"starter", "growth", "enterprise"} <= ids


@pytest.mark.asyncio
async def test_subscription_mock(client):
    r = await client.get("/api/v1/billing/subscription")
    assert r.status_code == 200
    body = r.json()
    assert body["backend"] == "mock"
    assert body["status"] == "active"
    assert body["seats"] >= 1


@pytest.mark.asyncio
async def test_checkout_returns_url(client):
    r = await client.post(
        "/api/v1/billing/checkout", json={"plan_id": "growth", "seats": 3}
    )
    assert r.status_code == 200
    assert "plan=growth" in r.json()["url"]
    assert "seats=3" in r.json()["url"]


@pytest.mark.asyncio
async def test_checkout_unknown_plan_400(client):
    r = await client.post("/api/v1/billing/checkout", json={"plan_id": "nope"})
    assert r.status_code == 400
