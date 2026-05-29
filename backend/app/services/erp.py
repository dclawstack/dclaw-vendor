"""Procurement / ERP integration (Phase 6, V6.4).

An ``ErpConnector`` abstraction with two backends behind it:

- **MockErpConnector** (default) — returns a small fixed set of external POs and
  invoices, so sync / matching / reconciliation are exercisable end-to-end in
  dev/CI without any external system.
- **HttpErpConnector** — talks to a real ERP REST API. Wired and ready; it only
  activates when ``ERP_BACKEND=http`` and ``ERP_BASE_URL``/``ERP_API_KEY`` are set.

Reconciliation is a pure function (``reconcile``) so it's trivially testable: it
matches external invoices to local POs by ``external_ref`` and flags variances
(over/under-billed) and unmatched invoices.
"""

from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import settings
from app.models.purchase_order import PurchaseOrder
from app.schemas.integration import (
    ExternalInvoice,
    ExternalPO,
    ReconciliationResult,
    ReconciliationRow,
)

VARIANCE_TOLERANCE = 0.01  # treat sub-cent differences as matched


class ErpConnector(Protocol):
    def pull_purchase_orders(self) -> list[ExternalPO]: ...
    def fetch_invoices(self) -> list[ExternalInvoice]: ...
    def push_purchase_order(self, po: PurchaseOrder) -> str: ...


class MockErpConnector:
    """Deterministic sample data for dev/CI."""

    def pull_purchase_orders(self) -> list[ExternalPO]:
        return [
            ExternalPO(external_ref="ERP-1001", vendor_name="Acme Corp", total=12000.0, status="sent"),
            ExternalPO(external_ref="ERP-1002", vendor_name="Globex", total=4500.0, status="received"),
        ]

    def fetch_invoices(self) -> list[ExternalInvoice]:
        return [
            ExternalInvoice(external_ref="ERP-1001", invoice_number="INV-9001", amount=12000.0, vendor_name="Acme Corp"),
            ExternalInvoice(external_ref="ERP-1002", invoice_number="INV-9002", amount=4800.0, vendor_name="Globex"),
            ExternalInvoice(external_ref="ERP-9999", invoice_number="INV-9003", amount=300.0, vendor_name="Unknown"),
        ]

    def push_purchase_order(self, po: PurchaseOrder) -> str:
        return po.external_ref or f"ERP-LOCAL-{str(po.id)[:8]}"


class HttpErpConnector:
    def __init__(self):
        self.base = settings.erp_base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.erp_api_key}"}

    def _get(self, path: str) -> list[dict]:
        with httpx.Client(timeout=15.0, headers=self.headers) as client:
            resp = client.get(f"{self.base}{path}")
            resp.raise_for_status()
            return resp.json()

    def pull_purchase_orders(self) -> list[ExternalPO]:
        return [ExternalPO(**row) for row in self._get("/purchase-orders")]

    def fetch_invoices(self) -> list[ExternalInvoice]:
        return [ExternalInvoice(**row) for row in self._get("/invoices")]

    def push_purchase_order(self, po: PurchaseOrder) -> str:
        payload = {"total": po.total, "status": po.status.value, "ref": str(po.id)}
        with httpx.Client(timeout=15.0, headers=self.headers) as client:
            resp = client.post(f"{self.base}/purchase-orders", json=payload)
            resp.raise_for_status()
            return resp.json().get("external_ref", "")


def get_connector() -> ErpConnector:
    if settings.erp_backend == "http" and settings.erp_base_url:
        return HttpErpConnector()
    return MockErpConnector()


def is_live() -> bool:
    return settings.erp_backend == "http" and bool(settings.erp_base_url)


def reconcile(
    invoices: list[ExternalInvoice], pos: list[PurchaseOrder]
) -> ReconciliationResult:
    """3-way-match-lite: invoice vs PO total, keyed on external_ref."""
    po_by_ref = {p.external_ref: p for p in pos if p.external_ref}
    rows: list[ReconciliationRow] = []
    matched = discrepancies = unmatched = 0
    for inv in invoices:
        po = po_by_ref.get(inv.external_ref)
        if po is None:
            rows.append(
                ReconciliationRow(
                    external_ref=inv.external_ref,
                    invoice_number=inv.invoice_number,
                    invoice_amount=inv.amount,
                    po_total=None,
                    variance=None,
                    status="unmatched",
                )
            )
            unmatched += 1
            continue
        variance = round(inv.amount - po.total, 2)
        if abs(variance) <= VARIANCE_TOLERANCE:
            status = "matched"
            matched += 1
        elif variance > 0:
            status = "over_billed"
            discrepancies += 1
        else:
            status = "under_billed"
            discrepancies += 1
        rows.append(
            ReconciliationRow(
                external_ref=inv.external_ref,
                invoice_number=inv.invoice_number,
                invoice_amount=inv.amount,
                po_total=po.total,
                variance=variance,
                status=status,
            )
        )
    return ReconciliationResult(
        rows=rows, matched=matched, discrepancies=discrepancies, unmatched=unmatched
    )
