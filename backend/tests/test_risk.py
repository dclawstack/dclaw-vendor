"""Phase 6 — V6.1 Risk Assessment: AI scoring, monitoring change alerts."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError
from app.services.risk import diff_factors


class FakeLLM:
    """Returns a RiskAnalysis with configurable factors."""

    def __init__(self, factors=None, level="medium", score=50.0, fail=False):
        self.factors = factors if factors is not None else [
            {"type": "financial", "severity": "high", "note": "thin margins"}
        ]
        self.level = level
        self.score = score
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        assert schema.__name__ == "RiskAnalysis"
        return schema(
            overall_level=self.level,
            overall_score=self.score,
            factors=self.factors,
            summary="Moderate risk vendor.",
        )


def use_llm(llm):
    app.dependency_overrides[get_llm] = lambda: llm


@pytest.fixture(autouse=True)
def _clear():
    yield
    app.dependency_overrides.pop(get_llm, None)


def test_diff_factors_detects_changes():
    prev = [
        {"type": "financial", "severity": "low"},
        {"type": "compliance", "severity": "medium"},
    ]
    cur = [
        {"type": "financial", "severity": "high"},  # increased
        {"type": "cybersecurity", "severity": "medium"},  # new
    ]  # compliance resolved
    changes = {c.type: c.change for c in diff_factors(prev, cur)}
    assert changes == {
        "financial": "increased",
        "cybersecurity": "new",
        "compliance": "resolved",
    }


@pytest.mark.asyncio
async def test_risk_types_catalog(client):
    r = await client.get("/api/v1/risk/types")
    assert r.status_code == 200
    assert len(r.json()) == 20
    assert "cybersecurity" in r.json()


@pytest.mark.asyncio
async def test_assess_persists_and_first_changes_are_new(client):
    use_llm(FakeLLM())
    vid = (await client.post("/api/v1/vendors", json={"name": "Acme"})).json()["id"]
    r = await client.post(f"/api/v1/risk/vendors/{vid}/assess")
    assert r.status_code == 200
    body = r.json()
    assert body["assessment"]["overall_level"] == "medium"
    assert body["assessment"]["factors"][0]["type"] == "financial"
    # first assessment -> all factors are "new"
    assert body["changes"][0]["change"] == "new"


@pytest.mark.asyncio
async def test_monitoring_change_alert(client):
    vid = (await client.post("/api/v1/vendors", json={"name": "Globex"})).json()["id"]
    use_llm(FakeLLM(factors=[{"type": "financial", "severity": "low", "note": "ok"}]))
    await client.post(f"/api/v1/risk/vendors/{vid}/assess")
    # second assessment escalates financial risk
    use_llm(FakeLLM(factors=[{"type": "financial", "severity": "high", "note": "deteriorated"}]))
    r = await client.post(f"/api/v1/risk/vendors/{vid}/assess")
    changes = {c["type"]: c["change"] for c in r.json()["changes"]}
    assert changes["financial"] == "increased"


@pytest.mark.asyncio
async def test_latest_and_history(client):
    use_llm(FakeLLM())
    vid = (await client.post("/api/v1/vendors", json={"name": "A"})).json()["id"]
    await client.post(f"/api/v1/risk/vendors/{vid}/assess")
    await client.post(f"/api/v1/risk/vendors/{vid}/assess")
    hist = await client.get(f"/api/v1/risk/vendors/{vid}/history")
    assert hist.json()["total"] == 2
    latest = await client.get(f"/api/v1/risk/vendors/{vid}/latest")
    assert latest.json()["overall_level"] == "medium"


@pytest.mark.asyncio
async def test_assess_llm_failure_502(client):
    use_llm(FakeLLM(fail=True))
    vid = (await client.post("/api/v1/vendors", json={"name": "Z"})).json()["id"]
    r = await client.post(f"/api/v1/risk/vendors/{vid}/assess")
    assert r.status_code == 502


@pytest.mark.asyncio
async def test_latest_404_when_none(client):
    vid = (await client.post("/api/v1/vendors", json={"name": "New"})).json()["id"]
    r = await client.get(f"/api/v1/risk/vendors/{vid}/latest")
    assert r.status_code == 404
