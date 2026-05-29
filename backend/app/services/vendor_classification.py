"""AI vendor classification (V3.1).

Classifies a vendor into the directory taxonomy (category / industry / tier)
using the LLM's structured-output helper. Exposed as a single + bulk operation
(the directory UI's "bulk classify"); not run automatically on every CRUD write
so that vendor create/update stay fast and provider-independent.
"""

from __future__ import annotations

import asyncio

from app.models.vendor import Vendor
from app.schemas.classification import VendorClassification, VendorClassificationResult
from app.services.llm import LLMService

_SYSTEM = (
    "You are a procurement taxonomy expert for a vendor-management platform. "
    "Classify the vendor into a concise spend category, its primary industry, and a "
    "strategic tier. Tiers: 'strategic' (mission-critical, hard to replace), "
    "'preferred' (favoured, high volume), 'approved' (vetted, routine use), "
    "'transactional' (one-off / commodity). Base it only on the details given; "
    "be decisive."
)


def build_context(vendor: Vendor) -> str:
    return (
        f"Vendor: {vendor.name}\n"
        f"Website: {vendor.website or 'n/a'}\n"
        f"Email: {vendor.email or 'n/a'}\n"
        f"Address: {vendor.address or 'n/a'}\n"
        f"Payment terms: {vendor.payment_terms or 'unspecified'}\n"
        f"Existing category: {vendor.category or 'none'}"
    )


async def classify_vendor(llm: LLMService, vendor: Vendor) -> VendorClassification:
    return await llm.structured(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": f"Classify this vendor:\n\n{build_context(vendor)}"},
        ],
        VendorClassification,
    )


async def classify_batch(
    llm: LLMService, vendors: list[Vendor], *, concurrency: int = 4
) -> list[VendorClassificationResult]:
    """Classify many vendors with bounded concurrency; per-vendor failures are
    captured rather than aborting the whole batch."""
    sem = asyncio.Semaphore(concurrency)

    async def one(vendor: Vendor) -> VendorClassificationResult:
        async with sem:
            try:
                classification = await classify_vendor(llm, vendor)
                return VendorClassificationResult(
                    vendor_id=vendor.id,
                    vendor_name=vendor.name,
                    classification=classification,
                )
            except Exception as e:  # noqa: BLE001 — record, don't abort the batch
                return VendorClassificationResult(
                    vendor_id=vendor.id, vendor_name=vendor.name, error=str(e)[:300]
                )

    return await asyncio.gather(*(one(v) for v in vendors))
