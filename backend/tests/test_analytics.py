"""Phase 6 — V6.3 Spend Analytics: aggregation + AI insights."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError


class FakeLLM:
    def __init__(self, fail=False):
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        assert schema.__name__ == "SpendInsightsAI"
        return schema(
            opportunities=[
                {"title": "Consolidate logistics", "category": "Logistics",
                 "rationale": "Two vendors, overlapping lanes", "estimated_savings": 5000.0}
            ],
            consolidation=[
                {"category": "Logistics", "vendors": ["A", "B"], "rationale": "merge"}
            ],
            summary="Consolidation could yield ~10%.",
        )


@pytest.fixture
def fake_llm():
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)


async def _vendor_with_po(client, name, category, total):
    vid = (await client.post("/api/v1/vendors", json={"name": name, "category": category})).json()["id"]
    await client.post(
        "/api/v1/purchase-orders",
        json={
            "vendor_id": vid,
            "status": "sent",
            "line_items": [{"product_name": "x", "quantity": 1, "unit_price": total}],
        },
    )
    return vid


@pytest.mark.asyncio
async def test_spend_summary_aggregates(client):
    await _vendor_with_po(client, "A", "Logistics", 1000.0)
    await _vendor_with_po(client, "B", "Logistics", 3000.0)
    await _vendor_with_po(client, "C", "IT Services", 2000.0)
    r = await client.get("/api/v1/analytics/spend")
    assert r.status_code == 200
    body = r.json()
    assert body["total_spend"] == 6000.0
    assert body["po_count"] == 3
    cats = {b["key"]: b["spend"] for b in body["by_category"]}
    assert cats == {"Logistics": 4000.0, "IT Services": 2000.0}
    # by_category sorted by spend desc
    assert body["by_category"][0]["key"] == "Logistics"


@pytest.mark.asyncio
async def test_spend_excludes_cancelled(client):
    vid = (await client.post("/api/v1/vendors", json={"name": "A"})).json()["id"]
    po = (
        await client.post(
            "/api/v1/purchase-orders",
            json={"vendor_id": vid, "line_items": [{"product_name": "x", "quantity": 1, "unit_price": 500}]},
        )
    ).json()
    await client.patch(f"/api/v1/purchase-orders/{po['id']}", json={"status": "cancelled"})
    r = await client.get("/api/v1/analytics/spend")
    assert r.json()["total_spend"] == 0.0
    assert r.json()["po_count"] == 0


@pytest.mark.asyncio
async def test_insights_computes_target(client, fake_llm):
    await _vendor_with_po(client, "A", "Logistics", 10000.0)
    r = await client.post("/api/v1/analytics/spend/insights")
    assert r.status_code == 200
    body = r.json()
    assert body["total_spend"] == 10000.0
    assert body["target_savings"] == 1000.0  # 10%
    assert body["opportunities"][0]["estimated_savings"] == 5000.0


@pytest.mark.asyncio
async def test_insights_llm_failure_502(client):
    app.dependency_overrides[get_llm] = lambda: FakeLLM(fail=True)
    try:
        r = await client.post("/api/v1/analytics/spend/insights")
        assert r.status_code == 502
    finally:
        app.dependency_overrides.pop(get_llm, None)
