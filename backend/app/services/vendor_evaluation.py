"""Vendor evaluation engine (V2.2).

Builds a compact context from a vendor and its purchase orders, then asks the
LLM for a structured `VendorEvaluation` (risk flags + performance outlook +
summary + recommendation). Supports bounded-concurrency batch evaluation.
"""

from __future__ import annotations

import asyncio

from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.schemas.evaluation import VendorEvaluation, VendorEvaluationResult
from app.services.llm import LLMService

_SYSTEM = (
    "You are a procurement risk analyst for a vendor-management platform. "
    "Given a vendor's profile and purchase-order history, assess procurement risk "
    "objectively and concisely. Blacklisted status is high risk; long payment terms "
    "and cancelled/overdue orders raise risk; a healthy received-order history lowers it."
)


def build_context(vendor: Vendor, pos: list[PurchaseOrder]) -> str:
    by_status: dict[str, int] = {}
    total_value = 0.0
    for po in pos:
        by_status[po.status.value] = by_status.get(po.status.value, 0) + 1
        total_value += po.total or 0.0
    status_line = ", ".join(f"{k}={v}" for k, v in sorted(by_status.items())) or "none"
    return (
        f"Vendor: {vendor.name}\n"
        f"Status: {vendor.status.value}\n"
        f"Payment terms: {vendor.payment_terms or 'unspecified'}\n"
        f"Contact: {vendor.contact_name or 'n/a'} <{vendor.email or 'n/a'}>\n"
        f"Purchase orders: {len(pos)} (by status: {status_line})\n"
        f"Total PO value: ${total_value:,.2f}"
    )


async def evaluate_vendor(
    llm: LLMService, vendor: Vendor, pos: list[PurchaseOrder]
) -> VendorEvaluation:
    context = build_context(vendor, pos)
    return await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Evaluate this vendor:\n\n{context}"},
        ],
        VendorEvaluation,
    )


async def evaluate_batch(
    llm: LLMService,
    vendors_with_pos: list[tuple[Vendor, list[PurchaseOrder]]],
    *,
    concurrency: int = 4,
) -> list[VendorEvaluationResult]:
    """Evaluate many vendors with bounded concurrency. Per-vendor failures are
    captured rather than aborting the whole batch."""
    sem = asyncio.Semaphore(concurrency)

    async def one(vendor: Vendor, pos: list[PurchaseOrder]) -> VendorEvaluationResult:
        async with sem:
            try:
                evaluation = await evaluate_vendor(llm, vendor, pos)
                return VendorEvaluationResult(
                    vendor_id=vendor.id, vendor_name=vendor.name, evaluation=evaluation
                )
            except Exception as e:  # noqa: BLE001 — record, don't abort the batch
                return VendorEvaluationResult(
                    vendor_id=vendor.id, vendor_name=vendor.name, error=str(e)[:300]
                )

    return await asyncio.gather(*(one(v, p) for v, p in vendors_with_pos))
