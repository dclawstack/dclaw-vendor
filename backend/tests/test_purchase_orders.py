import pytest


async def _make_vendor(client, name="Acme"):
    return (await client.post("/api/v1/vendors", json={"name": name})).json()["id"]


@pytest.mark.asyncio
async def test_create_po_with_line_items_computes_total(client):
    vid = await _make_vendor(client)
    resp = await client.post(
        "/api/v1/purchase-orders",
        json={
            "vendor_id": vid,
            "notes": "Q3 order",
            "line_items": [
                {"product_name": "Widget", "quantity": 3, "unit_price": 10.0},
                {"product_name": "Gadget", "quantity": 2, "unit_price": 5.5},
            ],
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "draft"
    assert body["total"] == 41.0  # 3*10 + 2*5.5
    assert len(body["line_items"]) == 2


@pytest.mark.asyncio
async def test_create_po_unknown_vendor_400(client):
    resp = await client.post(
        "/api/v1/purchase-orders",
        json={"vendor_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_po_without_vendor_allowed(client):
    resp = await client.post("/api/v1/purchase-orders", json={})
    assert resp.status_code == 201
    assert resp.json()["vendor_id"] is None
    assert resp.json()["total"] == 0


@pytest.mark.asyncio
async def test_update_po_status_and_vendor_filter(client):
    v1 = await _make_vendor(client, "One")
    v2 = await _make_vendor(client, "Two")
    po1 = (await client.post("/api/v1/purchase-orders", json={"vendor_id": v1})).json()["id"]
    await client.post("/api/v1/purchase-orders", json={"vendor_id": v2})

    patched = await client.patch(f"/api/v1/purchase-orders/{po1}", json={"status": "sent"})
    assert patched.json()["status"] == "sent"

    by_vendor = await client.get("/api/v1/purchase-orders", params={"vendor_id": v1})
    assert by_vendor.json()["total"] == 1

    by_status = await client.get("/api/v1/purchase-orders", params={"status": "sent"})
    assert by_status.json()["total"] == 1


@pytest.mark.asyncio
async def test_delete_po(client):
    po = (await client.post("/api/v1/purchase-orders", json={})).json()["id"]
    assert (await client.delete(f"/api/v1/purchase-orders/{po}")).status_code == 204
    assert (await client.get(f"/api/v1/purchase-orders/{po}")).status_code == 404
