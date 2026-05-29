"""Phase 6 — V6.4 Procurement Integration: sync, matching, reconciliation."""

import pytest

from app.models.enums import POStatus
from app.schemas.integration import ExternalInvoice
from app.services import erp


class _PO:
    def __init__(self, external_ref, total):
        self.external_ref = external_ref
        self.total = total


def test_reconcile_classifies_rows():
    invoices = [
        ExternalInvoice(external_ref="R1", invoice_number="I1", amount=100.0, vendor_name="A"),
        ExternalInvoice(external_ref="R2", invoice_number="I2", amount=120.0, vendor_name="B"),
        ExternalInvoice(external_ref="R3", invoice_number="I3", amount=90.0, vendor_name="C"),
        ExternalInvoice(external_ref="RX", invoice_number="I4", amount=50.0, vendor_name="D"),
    ]
    pos = [_PO("R1", 100.0), _PO("R2", 100.0), _PO("R3", 100.0)]
    result = erp.reconcile(invoices, pos)
    by_ref = {r.external_ref: r.status for r in result.rows}
    assert by_ref["R1"] == "matched"
    assert by_ref["R2"] == "over_billed"
    assert by_ref["R3"] == "under_billed"
    assert by_ref["RX"] == "unmatched"
    assert result.matched == 1 and result.discrepancies == 2 and result.unmatched == 1


@pytest.mark.asyncio
async def test_status_mock(client):
    r = await client.get("/api/v1/integration/status")
    assert r.status_code == 200
    assert r.json()["backend"] == "mock"
    assert r.json()["connected"] is True


@pytest.mark.asyncio
async def test_sync_creates_then_updates_and_links_vendor(client):
    # a vendor whose name matches the mock connector's "Acme Corp"
    await client.post("/api/v1/vendors", json={"name": "Acme Corp"})
    first = await client.post("/api/v1/integration/sync")
    body = first.json()
    assert body["pulled"] == 2 and body["created"] == 2 and body["updated"] == 0
    # synced PO is linked to the matching vendor + carries external_ref
    pos = (await client.get("/api/v1/purchase-orders")).json()["items"]
    acme_po = next(p for p in pos if p["external_ref"] == "ERP-1001")
    assert acme_po["vendor_id"] is not None

    # second sync updates, doesn't duplicate
    second = await client.post("/api/v1/integration/sync")
    assert second.json()["created"] == 0 and second.json()["updated"] == 2


@pytest.mark.asyncio
async def test_reconciliation_after_sync(client):
    await client.post("/api/v1/integration/sync")
    r = await client.get("/api/v1/integration/reconciliation")
    body = r.json()
    # mock: ERP-1001 matches (12000), ERP-1002 over-billed (4800 vs 4500), ERP-9999 unmatched
    assert body["matched"] == 1
    assert body["discrepancies"] == 1
    assert body["unmatched"] == 1
