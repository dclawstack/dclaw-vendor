"""Phase 7 — V7.4 Audit & Compliance: findings, closure validation."""

import pytest


async def _audit(client, name="Acme"):
    vid = (await client.post("/api/v1/vendors", json={"name": name})).json()["id"]
    aid = (
        await client.post(
            "/api/v1/audits",
            json={"vendor_id": vid, "title": "Annual SOC2", "auditor": "Jane"},
        )
    ).json()["id"]
    return vid, aid


@pytest.mark.asyncio
async def test_create_audit_default_scheduled(client):
    _, aid = await _audit(client)
    r = await client.get(f"/api/v1/audits/{aid}")
    assert r.json()["status"] == "scheduled"
    assert r.json()["auditor"] == "Jane"


@pytest.mark.asyncio
async def test_create_missing_vendor_404(client):
    r = await client.post(
        "/api/v1/audits",
        json={"vendor_id": "00000000-0000-0000-0000-000000000000", "title": "x"},
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_findings_and_closure_validation(client):
    _, aid = await _audit(client)
    f1 = (
        await client.post(
            f"/api/v1/audits/{aid}/findings",
            json={"description": "Missing MFA", "severity": "high"},
        )
    ).json()
    # cannot close with an open finding
    blocked = await client.post(f"/api/v1/audits/{aid}/close")
    assert blocked.status_code == 409

    # close the finding -> stamps closed_at
    upd = await client.patch(
        f"/api/v1/audits/findings/{f1['id']}",
        json={"status": "closed", "remediation": "MFA enforced"},
    )
    assert upd.json()["status"] == "closed"
    assert upd.json()["closed_at"] is not None

    # now closure succeeds
    closed = await client.post(f"/api/v1/audits/{aid}/close")
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_cannot_close_twice(client):
    _, aid = await _audit(client)
    await client.post(f"/api/v1/audits/{aid}/close")  # no findings -> closes
    again = await client.post(f"/api/v1/audits/{aid}/close")
    assert again.status_code == 409


@pytest.mark.asyncio
async def test_list_filter_and_delete(client):
    vid, aid = await _audit(client)
    lst = await client.get("/api/v1/audits", params={"vendor_id": vid})
    assert lst.json()["total"] == 1
    filtered = await client.get("/api/v1/audits", params={"status": "scheduled"})
    assert filtered.json()["total"] == 1
    d = await client.delete(f"/api/v1/audits/{aid}")
    assert d.status_code == 204
    assert (await client.get(f"/api/v1/audits/{aid}")).status_code == 404
