import pytest


async def _make_po(client):
    return (await client.post("/api/v1/purchase-orders", json={})).json()["id"]


@pytest.mark.asyncio
async def test_create_line_item_recomputes_total(client):
    po = await _make_po(client)
    resp = await client.post(
        "/api/v1/po-line-items",
        json={"po_id": po, "product_name": "Bolt", "quantity": 4, "unit_price": 2.5},
    )
    assert resp.status_code == 201
    assert resp.json()["po_id"] == po

    po_body = (await client.get(f"/api/v1/purchase-orders/{po}")).json()
    assert po_body["total"] == 10.0


@pytest.mark.asyncio
async def test_create_line_item_unknown_po_400(client):
    resp = await client.post(
        "/api/v1/po-line-items",
        json={"po_id": "00000000-0000-0000-0000-000000000000", "product_name": "X"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_receive_tracking_patch(client):
    po = await _make_po(client)
    item = (
        await client.post(
            "/api/v1/po-line-items",
            json={"po_id": po, "product_name": "Pipe", "quantity": 10, "unit_price": 3.0},
        )
    ).json()
    patched = await client.patch(
        f"/api/v1/po-line-items/{item['id']}", json={"received_qty": 6}
    )
    assert patched.status_code == 200
    assert patched.json()["received_qty"] == 6
    # price change recomputes total
    repriced = await client.patch(
        f"/api/v1/po-line-items/{item['id']}", json={"unit_price": 4.0}
    )
    assert repriced.json()["unit_price"] == 4.0
    assert (await client.get(f"/api/v1/purchase-orders/{po}")).json()["total"] == 40.0


@pytest.mark.asyncio
async def test_delete_line_item_recomputes_total(client):
    po = await _make_po(client)
    a = (await client.post("/api/v1/po-line-items", json={"po_id": po, "product_name": "A", "quantity": 1, "unit_price": 10})).json()
    await client.post("/api/v1/po-line-items", json={"po_id": po, "product_name": "B", "quantity": 1, "unit_price": 5})
    assert (await client.get(f"/api/v1/purchase-orders/{po}")).json()["total"] == 15.0

    assert (await client.delete(f"/api/v1/po-line-items/{a['id']}")).status_code == 204
    assert (await client.get(f"/api/v1/purchase-orders/{po}")).json()["total"] == 5.0


@pytest.mark.asyncio
async def test_list_line_items_by_po(client):
    po = await _make_po(client)
    await client.post("/api/v1/po-line-items", json={"po_id": po, "product_name": "A"})
    await client.post("/api/v1/po-line-items", json={"po_id": po, "product_name": "B"})
    resp = await client.get("/api/v1/po-line-items", params={"po_id": po})
    assert resp.json()["total"] == 2
