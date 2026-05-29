"""Phase 7 — V7.2 Sustainability scoring."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError


class FakeLLM:
    def __init__(self, e=80.0, s=70.0, g=90.0, fail=False):
        self.e, self.s, self.g, self.fail = e, s, g, fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        assert schema.__name__ == "SustainabilityAssessment"
        return schema(
            environmental_score=self.e,
            social_score=self.s,
            governance_score=self.g,
            carbon_footprint=1234.5,
            targets=[{"target": "Cut Scope 1 by 10%", "by": "2027"}],
            summary="Improving ESG posture.",
        )


def use_llm(llm):
    app.dependency_overrides[get_llm] = lambda: llm


@pytest.fixture(autouse=True)
def _clear():
    yield
    app.dependency_overrides.pop(get_llm, None)


@pytest.mark.asyncio
async def test_score_computes_overall(client):
    use_llm(FakeLLM(e=90.0, s=60.0, g=90.0))
    vid = (await client.post("/api/v1/vendors", json={"name": "Acme"})).json()["id"]
    r = await client.post("/api/v1/sustainability/vendors/%s/score" % vid, json={"period": "2026-Q2"})
    assert r.status_code == 200
    body = r.json()
    assert body["overall_score"] == 80.0  # mean(90,60,90)
    assert body["carbon_footprint"] == 1234.5
    assert body["targets"][0]["by"] == "2027"


@pytest.mark.asyncio
async def test_latest_and_history(client):
    use_llm(FakeLLM())
    vid = (await client.post("/api/v1/vendors", json={"name": "A"})).json()["id"]
    await client.post(f"/api/v1/sustainability/vendors/{vid}/score")
    await client.post(f"/api/v1/sustainability/vendors/{vid}/score")
    hist = await client.get(f"/api/v1/sustainability/vendors/{vid}/history")
    assert hist.json()["total"] == 2
    latest = await client.get(f"/api/v1/sustainability/vendors/{vid}/latest")
    assert latest.json()["environmental_score"] == 80.0


@pytest.mark.asyncio
async def test_latest_404(client):
    vid = (await client.post("/api/v1/vendors", json={"name": "N"})).json()["id"]
    r = await client.get(f"/api/v1/sustainability/vendors/{vid}/latest")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_score_llm_failure_502(client):
    use_llm(FakeLLM(fail=True))
    vid = (await client.post("/api/v1/vendors", json={"name": "Z"})).json()["id"]
    r = await client.post(f"/api/v1/sustainability/vendors/{vid}/score")
    assert r.status_code == 502
