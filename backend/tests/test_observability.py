"""Phase 8 — V8.3 Monitoring: Prometheus /metrics."""

import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    # generate a request so the counter has something to report
    await client.get("/health/")
    r = await client.get("/metrics")
    assert r.status_code == 200
    body = r.text
    assert "http_requests_total" in body
    assert "http_request_duration_seconds" in body


@pytest.mark.asyncio
async def test_metrics_counts_requests(client):
    await client.get("/api/v1/vendors")
    r = await client.get("/metrics")
    # the templated route path is used as a label (bounded cardinality)
    assert "/api/v1/vendors" in r.text
