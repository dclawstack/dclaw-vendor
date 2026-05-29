"""Schemas for procurement / ERP integration (Phase 6, V6.4)."""

from typing import Literal

from pydantic import BaseModel


class ExternalPO(BaseModel):
    """A purchase order as represented in the external ERP."""

    external_ref: str
    vendor_name: str
    total: float
    status: str


class ExternalInvoice(BaseModel):
    external_ref: str  # the PO reference this invoice bills against
    invoice_number: str
    amount: float
    vendor_name: str


class IntegrationStatus(BaseModel):
    backend: str  # "mock" | "http"
    connected: bool
    base_url: str | None


class SyncResult(BaseModel):
    pulled: int
    created: int
    updated: int


class ReconciliationRow(BaseModel):
    external_ref: str
    invoice_number: str
    invoice_amount: float
    po_total: float | None
    variance: float | None  # invoice_amount - po_total
    status: Literal["matched", "over_billed", "under_billed", "unmatched"]


class ReconciliationResult(BaseModel):
    rows: list[ReconciliationRow]
    matched: int
    discrepancies: int
    unmatched: int
