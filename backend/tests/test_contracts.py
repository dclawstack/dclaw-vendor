"""Phase 6 — V6.2 Contract Management: CRUD, status derivation, renewals, AI extract."""

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
        assert schema.__name__ == "ExtractedTerms"
        return schema(
            payment_terms="Net 45",
            sla="99.9% uptime",
            termination_clause="30 days notice",
            renewal_terms="auto-renew annually",
            liability="capped at fees",
            pricing="$10k/mo",
        )


@pytest.fixture
def fake_llm():
    app.dependency_overrides[get_llm] = lambda: FakeLLM()
    yield
    app.dependency_overrides.pop(get_llm, None)


async def _vendor(client, name="Acme"):
    return (await client.post("/api/v1/vendors", json={"name": name})).json()["id"]


@pytest.mark.asyncio
async def test_create_status_from_dates(client):
    vid = await _vendor(client)
    # far-future end date -> active
    r = await client.post(
        "/api/v1/contracts",
        json={"vendor_id": vid, "title": "MSA", "end_date": "2030-01-01"},
    )
    assert r.status_code == 201
    assert r.json()["status"] == "active"
    # past end date -> expired
    r2 = await client.post(
        "/api/v1/contracts",
        json={"vendor_id": vid, "title": "Old", "end_date": "2020-01-01"},
    )
    assert r2.json()["status"] == "expired"


@pytest.mark.asyncio
async def test_create_missing_vendor_404(client):
    r = await client.post(
        "/api/v1/contracts",
        json={"vendor_id": "00000000-0000-0000-0000-000000000000", "title": "X"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_list_filter_and_get(client):
    vid = await _vendor(client)
    cid = (
        await client.post(
            "/api/v1/contracts", json={"vendor_id": vid, "title": "MSA", "end_date": "2030-01-01"}
        )
    ).json()["id"]
    lst = await client.get("/api/v1/contracts", params={"vendor_id": vid})
    assert lst.json()["total"] == 1
    got = await client.get(f"/api/v1/contracts/{cid}")
    assert got.json()["title"] == "MSA"


@pytest.mark.asyncio
async def test_update_reders_status(client):
    vid = await _vendor(client)
    cid = (
        await client.post(
            "/api/v1/contracts", json={"vendor_id": vid, "title": "C", "end_date": "2030-01-01"}
        )
    ).json()["id"]
    # manual terminate is preserved
    r = await client.patch(f"/api/v1/contracts/{cid}", json={"status": "terminated"})
    assert r.json()["status"] == "terminated"


@pytest.mark.asyncio
async def test_renewals_endpoint(client):
    vid = await _vendor(client)
    await client.post(
        "/api/v1/contracts",
        json={"vendor_id": vid, "title": "Soon", "end_date": "2026-06-15"},
    )
    r = await client.get("/api/v1/contracts/renewals")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1
    assert items[0]["title"] == "Soon"
    assert items[0]["days_to_expiry"] is not None


@pytest.mark.asyncio
async def test_extract_terms(client, fake_llm):
    vid = await _vendor(client)
    cid = (
        await client.post("/api/v1/contracts", json={"vendor_id": vid, "title": "C"})
    ).json()["id"]
    r = await client.post(
        f"/api/v1/contracts/{cid}/extract",
        json={"text": "Payment Net 45. Auto-renew annually. 30 days termination notice."},
    )
    assert r.status_code == 200
    assert r.json()["key_terms"]["payment_terms"] == "Net 45"


@pytest.mark.asyncio
async def test_delete_contract(client):
    vid = await _vendor(client)
    cid = (
        await client.post("/api/v1/contracts", json={"vendor_id": vid, "title": "C"})
    ).json()["id"]
    d = await client.delete(f"/api/v1/contracts/{cid}")
    assert d.status_code == 204
    assert (await client.get(f"/api/v1/contracts/{cid}")).status_code == 404
