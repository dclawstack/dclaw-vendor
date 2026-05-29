"""Phase 7 — V7.1 Diversity tracking + reporting."""

import pytest


async def _vendor_with_po(client, name, total, **diversity):
    vid = (await client.post("/api/v1/vendors", json={"name": name, **diversity})).json()["id"]
    if total:
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
async def test_diversity_fields_persist(client):
    r = await client.post(
        "/api/v1/vendors",
        json={
            "name": "DiverseCo",
            "diverse_owned": True,
            "diversity_categories": ["women_owned", "minority_owned"],
            "diversity_certified": True,
            "certification_body": "NMSDC",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["diverse_owned"] is True
    assert body["diversity_categories"] == ["women_owned", "minority_owned"]
    assert body["certification_body"] == "NMSDC"


@pytest.mark.asyncio
async def test_diversity_report(client):
    await _vendor_with_po(
        client, "A", 3000.0,
        diverse_owned=True, diversity_categories=["women_owned"], diversity_certified=True,
    )
    await _vendor_with_po(
        client, "B", 1000.0,
        diverse_owned=True, diversity_categories=["veteran_owned", "women_owned"],
    )
    await _vendor_with_po(client, "C", 6000.0)  # not diverse

    r = await client.get("/api/v1/diversity/report")
    assert r.status_code == 200
    body = r.json()
    assert body["total_spend"] == 10000.0
    assert body["diverse_spend"] == 4000.0
    assert body["diverse_spend_pct"] == 40.0
    assert body["diverse_vendor_count"] == 2
    assert body["certified_count"] == 1
    cats = {c["category"]: c for c in body["by_category"]}
    assert cats["women_owned"]["vendor_count"] == 2
    assert cats["women_owned"]["spend"] == 4000.0
    assert cats["veteran_owned"]["spend"] == 1000.0
