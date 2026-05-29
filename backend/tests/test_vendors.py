import pytest


@pytest.mark.asyncio
async def test_create_and_get_vendor(client):
    resp = await client.post(
        "/api/v1/vendors",
        json={"name": "Acme Corp", "email": "ap@acme.test", "payment_terms": "Net 30"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Acme Corp"
    assert body["status"] == "active"
    vid = body["id"]

    got = await client.get(f"/api/v1/vendors/{vid}")
    assert got.status_code == 200
    assert got.json()["email"] == "ap@acme.test"


@pytest.mark.asyncio
async def test_get_missing_vendor_404(client):
    resp = await client.get("/api/v1/vendors/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_vendor(client):
    vid = (await client.post("/api/v1/vendors", json={"name": "Beta"})).json()["id"]
    resp = await client.patch(
        f"/api/v1/vendors/{vid}", json={"status": "blacklisted", "phone": "555-1234"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "blacklisted"
    assert resp.json()["phone"] == "555-1234"
    # untouched field preserved
    assert resp.json()["name"] == "Beta"


@pytest.mark.asyncio
async def test_delete_vendor(client):
    vid = (await client.post("/api/v1/vendors", json={"name": "Gamma"})).json()["id"]
    assert (await client.delete(f"/api/v1/vendors/{vid}")).status_code == 204
    assert (await client.get(f"/api/v1/vendors/{vid}")).status_code == 404


@pytest.mark.asyncio
async def test_list_search_and_status_filter(client):
    await client.post("/api/v1/vendors", json={"name": "Alpha Foods", "email": "a@x.test"})
    await client.post("/api/v1/vendors", json={"name": "Beta Metals", "status": "inactive"})
    await client.post("/api/v1/vendors", json={"name": "Gamma Foods"})

    all_v = await client.get("/api/v1/vendors")
    assert all_v.json()["total"] == 3

    search = await client.get("/api/v1/vendors", params={"search": "Foods"})
    assert search.json()["total"] == 2

    inactive = await client.get("/api/v1/vendors", params={"status": "inactive"})
    assert inactive.json()["total"] == 1
    assert inactive.json()["items"][0]["name"] == "Beta Metals"


@pytest.mark.asyncio
async def test_pagination(client):
    for i in range(5):
        await client.post("/api/v1/vendors", json={"name": f"V{i}"})
    page = await client.get("/api/v1/vendors", params={"limit": 2, "offset": 0})
    assert page.json()["total"] == 5
    assert len(page.json()["items"]) == 2


@pytest.mark.asyncio
async def test_invalid_status_rejected(client):
    resp = await client.post("/api/v1/vendors", json={"name": "X", "status": "bogus"})
    assert resp.status_code == 422
