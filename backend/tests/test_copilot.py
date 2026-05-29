import pytest

from app.api.main import app
from app.api.v1.copilot import get_llm
from app.services.llm import LLMError


class FakeLLM:
    """Schema-aware stub: returns a CopilotReply (echoing the grounding context
    so tests can assert retrieval fed the prompt) or a VendorEvaluation."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        if schema.__name__ == "CopilotReply":
            system = messages[0]["content"] if messages else ""
            return schema(reply=system, suggested_actions=["Add a vendor", "Create a PO"])
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
async def test_chat_returns_reply_and_actions(client, fake_llm):
    # seed a vendor so retrieval has something to ground on
    await client.post("/api/v1/vendors", json={"name": "Acme Industrial"})
    r = await client.post(
        "/api/v1/copilot/chat",
        json={"messages": [{"role": "user", "content": "How many vendors do I have?"}]},
    )
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body["reply"], str) and body["reply"]
    assert body["suggested_actions"] == ["Add a vendor", "Create a PO"]
    # FakeLLM echoes the grounding context -> retrieval fed the prompt
    assert "Acme Industrial" in body["reply"]
    assert "Vendor workspace snapshot" in body["reply"]


@pytest.mark.asyncio
async def test_chat_with_vendor_focus(client, fake_llm):
    vid = (await client.post("/api/v1/vendors", json={"name": "Globex"})).json()["id"]
    r = await client.post(
        "/api/v1/copilot/chat",
        json={
            "messages": [{"role": "user", "content": "Assess this vendor"}],
            "vendor_id": vid,
        },
    )
    assert r.status_code == 200
    assert "Focused vendor: Globex" in r.json()["reply"]


@pytest.mark.asyncio
async def test_chat_requires_messages(client, fake_llm):
    r = await client.post("/api/v1/copilot/chat", json={"messages": []})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_chat_llm_failure_502(client):
    app.dependency_overrides[get_llm] = lambda: FakeLLM(fail=True)
    try:
        await client.post("/api/v1/vendors", json={"name": "X"})
        r = await client.post(
            "/api/v1/copilot/chat",
            json={"messages": [{"role": "user", "content": "hi"}]},
        )
        assert r.status_code == 502
    finally:
        app.dependency_overrides.pop(get_llm, None)


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
