"""Copilot context retrieval (V2.3).

The vendor/PO dataset is small and fully structured, so the copilot is grounded
with **query-based retrieval** straight from the database (aggregates + the most
relevant vendors/POs) rather than a vector index. pgvector/Qdrant would only earn
its keep over large unstructured corpora — see the dev plan's "only if needed"
note. The retrieval surface is isolated here so it can be swapped for embeddings
later without touching the chat endpoint.
"""

from __future__ import annotations

import uuid
from collections import Counter

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import POStatus
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.repositories.vendor_repo import VendorRepository

_OPEN = {POStatus.draft, POStatus.sent, POStatus.partial}


async def build_copilot_context(
    db: AsyncSession,
    *,
    vendor_id: uuid.UUID | None = None,
    query: str | None = None,
    max_vendors: int = 8,
    max_pos: int = 8,
) -> str:
    vrepo = VendorRepository(db)
    prepo = PurchaseOrderRepository(db)

    vendors, vtotal = await vrepo.list_vendors(limit=500)
    pos, ptotal = await prepo.list_purchase_orders(limit=500)
    vname = {v.id: v.name for v in vendors}

    v_by_status = Counter(v.status.value for v in vendors)
    p_by_status = Counter(p.status.value for p in pos)
    total_spend = sum(p.total or 0.0 for p in pos)
    open_pos = sum(1 for p in pos if p.status in _OPEN)

    lines: list[str] = [
        "=== Vendor workspace snapshot ===",
        f"Vendors: {vtotal} ("
        + ", ".join(f"{k}={v}" for k, v in sorted(v_by_status.items()))
        + ")",
        f"Purchase orders: {ptotal} ("
        + ", ".join(f"{k}={v}" for k, v in sorted(p_by_status.items()))
        + f"), open={open_pos}, total spend=${total_spend:,.2f}",
    ]

    # Relevant vendors: filter by query if given, else most recent.
    relevant = vendors
    if query:
        q = query.lower()
        matched = [
            v
            for v in vendors
            if q in v.name.lower() or (v.email and q in v.email.lower())
        ]
        relevant = matched or vendors
    lines.append("Vendors:")
    for v in relevant[:max_vendors]:
        terms = v.payment_terms or "n/a"
        lines.append(f"- {v.name} [{v.status.value}] terms={terms} email={v.email or 'n/a'}")

    lines.append("Recent purchase orders:")
    for p in pos[:max_pos]:
        who = vname.get(p.vendor_id, "—") if p.vendor_id else "—"
        lines.append(
            f"- {str(p.id)[:8]} vendor={who} [{p.status.value}] "
            f"total=${p.total:,.2f} items={len(p.line_items)}"
        )

    if vendor_id is not None:
        focus = await vrepo.get_by_id(vendor_id)
        if focus is not None:
            lines.append(f"=== Focused vendor: {focus.name} ===")
            lines.append(
                f"status={focus.status.value}, terms={focus.payment_terms or 'n/a'}, "
                f"contact={focus.contact_name or 'n/a'} <{focus.email or 'n/a'}>"
            )
            fpos = list(focus.purchase_orders)
            lines.append(f"This vendor has {len(fpos)} purchase order(s):")
            for p in fpos[:max_pos]:
                lines.append(
                    f"- {str(p.id)[:8]} [{p.status.value}] total=${p.total:,.2f}"
                )

    return "\n".join(lines)
