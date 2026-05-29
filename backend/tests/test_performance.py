"""Phase 5 — Performance Tracking: AI scoring, composite, trend, benchmark."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError
from app.services.performance import compute_dimensions


class FakeLLM:
    """Returns a ScoredAssessment; KPI values default to `base` so dimension
    math is predictable, with optional overrides."""

    def __init__(self, base: float = 80.0, overrides: dict | None = None, fail=False):
        self.base = base
        self.overrides = overrides or {}
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        assert schema.__name__ == "ScoredAssessment"
        keys = [
            "defect_rate", "return_rate", "quality_audit",
            "on_time_delivery", "lead_time_adherence",
            "price_competitiveness", "cost_savings",
            "documentation", "certifications", "responsiveness",
        ]
        kpis = {k: self.overrides.get(k, self.base) for k in keys}
        return schema(kpis=kpis, summary="Solid, reliable supplier.")


def use_llm(llm):
    app.dependency_overrides[get_llm] = lambda: llm


@pytest.fixture(autouse=True)
def _clear():
    yield
    app.dependency_overrides.pop(get_llm, None)


async def _vendor(client, name="Acme", category=None):
    body = {"name": name}
    if category:
        body["category"] = category
    return (await client.post("/api/v1/vendors", json=body)).json()["id"]


def test_compute_dimensions_equal_weight():
    kpis = {
        "defect_rate": 90, "return_rate": 90, "quality_audit": 90,
        "on_time_delivery": 80, "lead_time_adherence": 80,
        "price_competitiveness": 70, "cost_savings": 70,
        "documentation": 60, "certifications": 60, "responsiveness": 60,
    }
    d = compute_dimensions(kpis)
    assert d["quality_score"] == 90.0
    assert d["delivery_score"] == 80.0
    assert d["cost_score"] == 70.0
    assert d["compliance_score"] == 60.0
    assert d["overall_score"] == 75.0


@pytest.mark.asyncio
async def test_score_persists_and_computes(client):
    use_llm(FakeLLM(base=80.0))
    vid = await _vendor(client)
    r = await client.post(f"/api/v1/performance/vendors/{vid}/score", json={"period": "2026-Q2"})
    assert r.status_code == 200
    body = r.json()
    assert body["period"] == "2026-Q2"
    assert body["overall_score"] == 80.0
    assert body["kpis"]["defect_rate"] == 80.0
    assert body["summary"]


@pytest.mark.asyncio
async def test_score_default_period(client):
    use_llm(FakeLLM())
    vid = await _vendor(client)
    r = await client.post(f"/api/v1/performance/vendors/{vid}/score")
    assert r.status_code == 200
    assert r.json()["period"].startswith("20") and "-Q" in r.json()["period"]


@pytest.mark.asyncio
async def test_score_missing_vendor_404(client):
    use_llm(FakeLLM())
    r = await client.post(
        "/api/v1/performance/vendors/00000000-0000-0000-0000-000000000000/score"
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_score_llm_failure_502(client):
    use_llm(FakeLLM(fail=True))
    vid = await _vendor(client)
    r = await client.post(f"/api/v1/performance/vendors/{vid}/score")
    assert r.status_code == 502


@pytest.mark.asyncio
async def test_trend_and_latest(client):
    use_llm(FakeLLM(base=70.0))
    vid = await _vendor(client)
    await client.post(f"/api/v1/performance/vendors/{vid}/score", json={"period": "2026-Q1"})
    use_llm(FakeLLM(base=90.0))
    await client.post(f"/api/v1/performance/vendors/{vid}/score", json={"period": "2026-Q2"})

    trend = await client.get(f"/api/v1/performance/vendors/{vid}/trend")
    pts = trend.json()
    assert [p["overall_score"] for p in pts] == [70.0, 90.0]  # oldest → newest

    latest = await client.get(f"/api/v1/performance/vendors/{vid}/latest")
    assert latest.json()["overall_score"] == 90.0


@pytest.mark.asyncio
async def test_latest_404_when_none(client):
    vid = await _vendor(client)
    r = await client.get(f"/api/v1/performance/vendors/{vid}/latest")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_benchmark_against_peers(client):
    use_llm(FakeLLM(base=90.0))
    a = await _vendor(client, "A", category="Logistics")
    await client.post(f"/api/v1/performance/vendors/{a}/score", json={"period": "2026-Q2"})
    use_llm(FakeLLM(base=70.0))
    b = await _vendor(client, "B", category="Logistics")
    await client.post(f"/api/v1/performance/vendors/{b}/score", json={"period": "2026-Q2"})

    r = await client.get(f"/api/v1/performance/vendors/{a}/benchmark")
    body = r.json()
    assert body["peer_group"] == "category:Logistics"
    assert body["vendor_overall"] == 90.0
    assert body["peer_count"] == 1
    assert body["peer_average"] == 70.0
    assert body["percentile"] == 100.0  # A scores at/above its one peer
