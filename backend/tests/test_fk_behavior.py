import pytest


@pytest.mark.asyncio
async def test_deleting_vendor_sets_po_vendor_id_null(client):
    """PO -> Vendor FK is ondelete=SET NULL: PO survives, vendor_id cleared."""
    vid = (await client.post("/api/v1/vendors", json={"name": "Acme"})).json()["id"]
    po = (await client.post("/api/v1/purchase-orders", json={"vendor_id": vid})).json()
    assert po["vendor_id"] == vid

    assert (await client.delete(f"/api/v1/vendors/{vid}")).status_code == 204

    after = await client.get(f"/api/v1/purchase-orders/{po['id']}")
    assert after.status_code == 200
    assert after.json()["vendor_id"] is None


@pytest.mark.asyncio
async def test_deleting_po_cascades_line_items(client):
    """POLineItem -> PO FK is ondelete=CASCADE: line items removed with the PO."""
    po = (
        await client.post(
            "/api/v1/purchase-orders",
            json={"line_items": [{"product_name": "Widget", "quantity": 1, "unit_price": 9.0}]},
        )
    ).json()
    po_id = po["id"]
    item_id = po["line_items"][0]["id"]

    assert (await client.delete(f"/api/v1/purchase-orders/{po_id}")).status_code == 204

    # line item is gone with its parent
    listing = await client.get("/api/v1/po-line-items", params={"po_id": po_id})
    assert listing.json()["total"] == 0
    assert (await client.patch(f"/api/v1/po-line-items/{item_id}", json={"received_qty": 1})).status_code == 404
