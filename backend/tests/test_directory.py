"""Phase 3 — Vendor Directory: classification, enrichment, facets, filters."""

import pytest

from app.api.deps import get_llm
from app.api.main import app
from app.services.llm import LLMError


class FakeLLM:
    """Schema-aware stub for VendorClassification + EnrichedProfile."""

    def __init__(self, fail: bool = False):
        self.fail = fail

    async def structured(self, messages, schema):
        if self.fail:
            raise LLMError("llm down")
        if schema.__name__ == "VendorClassification":
            return schema(
                category="IT Services",
                industry="Software",
                tier="strategic",
                rationale="Mission-critical software supplier.",
            )
        if schema.__name__ == "EnrichedProfile":
            return schema(
                company_size="51-200",
                founded_year=2010,
                headquarters="Austin, TX",
                industry="Software",
                description="Builds procurement software.",
            )
        raise AssertionError(f"unexpected schema {schema.__name__}")


@pytest.fixture
def fake_llm():
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)


@pytest.mark.asyncio
async def test_create_with_directory_fields(client):
    r = await client.post(
        "/api/v1/vendors",
        json={"name": "Globex", "tier": "preferred", "category": "Logistics", "website": "globex.test"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["tier"] == "preferred"
    assert body["category"] == "Logistics"
    assert body["website"] == "globex.test"
    assert body["enrichment"] is None


@pytest.mark.asyncio
async def test_classify_persists(client, fake_llm):
    vid = (await client.post("/api/v1/vendors", json={"name": "Acme"})).json()["id"]
    r = await client.post(f"/api/v1/vendors/{vid}/classify")
    assert r.status_code == 200
    assert r.json()["classification"]["tier"] == "strategic"
    # persisted onto the vendor
    got = await client.get(f"/api/v1/vendors/{vid}")
    assert got.json()["category"] == "IT Services"
    assert got.json()["tier"] == "strategic"
    assert got.json()["industry"] == "Software"


@pytest.mark.asyncio
async def test_classify_missing_404(client, fake_llm):
    r = await client.post(
        "/api/v1/vendors/00000000-0000-0000-0000-000000000000/classify"
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_classify_llm_failure_502(client):
    app.dependency_overrides[get_llm] = lambda: FakeLLM(fail=True)
    try:
        vid = (await client.post("/api/v1/vendors", json={"name": "Z"})).json()["id"]
        r = await client.post(f"/api/v1/vendors/{vid}/classify")
        assert r.status_code == 502
    finally:
        app.dependency_overrides.pop(get_llm, None)


@pytest.mark.asyncio
async def test_classify_batch_only_unclassified(client, fake_llm):
    await client.post("/api/v1/vendors", json={"name": "A"})
    await client.post("/api/v1/vendors", json={"name": "B", "tier": "approved"})
    r = await client.post("/api/v1/vendors/classify-batch")
    assert r.status_code == 200
    body = r.json()
    # only the one without a tier gets classified
    assert body["classified"] == 1 and body["failed"] == 0


@pytest.mark.asyncio
async def test_enrich_inferred_provenance(client, fake_llm):
    # no website / corp email -> inferred path, no network
    vid = (await client.post("/api/v1/vendors", json={"name": "Initech"})).json()["id"]
    r = await client.post(f"/api/v1/vendors/{vid}/enrich")
    assert r.status_code == 200
    enr = r.json()["enrichment"]
    assert enr["source"] == "inferred"
    assert enr["fetched_url"] is None
    assert enr["headquarters"] == "Austin, TX"
    # adopted industry + persisted
    got = await client.get(f"/api/v1/vendors/{vid}")
    assert got.json()["industry"] == "Software"
    assert got.json()["enrichment"]["company_size"] == "51-200"


@pytest.mark.asyncio
async def test_filter_by_category_and_tier(client):
    await client.post(
        "/api/v1/vendors", json={"name": "L1", "category": "Logistics", "tier": "approved"}
    )
    await client.post(
        "/api/v1/vendors", json={"name": "IT1", "category": "IT Services", "tier": "strategic"}
    )
    r = await client.get("/api/v1/vendors", params={"category": "Logistics"})
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["name"] == "L1"
    r = await client.get("/api/v1/vendors", params={"tier": "strategic"})
    assert r.json()["total"] == 1
    assert r.json()["items"][0]["name"] == "IT1"


@pytest.mark.asyncio
async def test_facets(client):
    await client.post(
        "/api/v1/vendors", json={"name": "A", "category": "Logistics", "tier": "approved"}
    )
    await client.post(
        "/api/v1/vendors", json={"name": "B", "category": "Logistics", "tier": "strategic"}
    )
    await client.post("/api/v1/vendors", json={"name": "C"})
    r = await client.get("/api/v1/vendors/facets")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    cats = {c["value"]: c["count"] for c in body["category"]}
    assert cats == {"Logistics": 2}
    tiers = {t["value"]: t["count"] for t in body["tier"]}
    assert tiers == {"approved": 1, "strategic": 1}
    statuses = {s["value"]: s["count"] for s in body["status"]}
    assert statuses["active"] == 3
