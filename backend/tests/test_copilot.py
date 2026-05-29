import pytest

from app.api.main import app
from app.api.v1.copilot import get_llm


class FakeLLM:
    def __init__(self, fail: bool = False):
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise RuntimeError("llm down")
        return schema(
            risk_level="low",
            risk_flags=[],
            performance_outlook="stable",
            summary="Healthy vendor.",
            recommendation="approve",
        )


@pytest.fixture
def fake_llm():
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)


@pytest.mark.asyncio
async def test_evaluate_vendor(client, fake_llm):
    vid = (await client.post("/api/v1/vendors", json={"name": "Acme"})).json()["id"]
    r = await client.post(f"/api/v1/copilot/vendors/{vid}/evaluate")
    assert r.status_code == 200
    body = r.json()
    assert body["vendor_name"] == "Acme"
    assert body["evaluation"]["risk_level"] == "low"
    assert body["evaluation"]["recommendation"] == "approve"


@pytest.mark.asyncio
async def test_evaluate_missing_vendor_404(client, fake_llm):
    r = await client.post(
        "/api/v1/copilot/vendors/00000000-0000-0000-0000-000000000000/evaluate"
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_batch(client, fake_llm):
    await client.post("/api/v1/vendors", json={"name": "A"})
    await client.post("/api/v1/vendors", json={"name": "B"})
    r = await client.post("/api/v1/copilot/vendors/evaluate-batch")
    assert r.status_code == 200
    body = r.json()
    assert body["evaluated"] == 2 and body["failed"] == 0
    assert len(body["results"]) == 2


@pytest.mark.asyncio
async def test_evaluate_batch_captures_failures(client):
    app.dependency_overrides[get_llm] = lambda: FakeLLM(fail=True)
    try:
        await client.post("/api/v1/vendors", json={"name": "A"})
        r = await client.post("/api/v1/copilot/vendors/evaluate-batch")
        assert r.status_code == 200
        body = r.json()
        assert body["failed"] == 1 and body["evaluated"] == 0
        assert body["results"][0]["error"]
        assert body["results"][0]["evaluation"] is None
    finally:
        app.dependency_overrides.pop(get_llm, None)
