from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.enums import POStatus
from app.models.purchase_order import PurchaseOrder
from app.models.vendor import Vendor
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.schemas.integration import (
    IntegrationStatus,
    ReconciliationResult,
    SyncResult,
)
from app.services import erp

router = APIRouter()


@router.get("/status", response_model=IntegrationStatus)
async def status():
    return IntegrationStatus(
        backend=settings.erp_backend,
        connected=erp.is_live() or settings.erp_backend == "mock",
        base_url=settings.erp_base_url or None,
    )


def _map_status(raw: str) -> POStatus:
    try:
        return POStatus(raw)
    except ValueError:
        return POStatus.draft


@router.post("/sync", response_model=SyncResult)
async def sync(db: AsyncSession = Depends(get_db)):
    """Pull external POs and upsert local ones, matched by external_ref (V6.4)."""
    external = erp.get_connector().pull_purchase_orders()

    existing = {
        po.external_ref: po
        for po in (await db.execute(select(PurchaseOrder).where(PurchaseOrder.external_ref.is_not(None)))).scalars()
    }
    vendors_by_name = {
        v.name: v for v in (await db.execute(select(Vendor))).scalars()
    }

    created = updated = 0
    for ext in external:
        vendor = vendors_by_name.get(ext.vendor_name)
        if ext.external_ref in existing:
            po = existing[ext.external_ref]
            po.total = ext.total
            po.status = _map_status(ext.status)
            if vendor:
                po.vendor_id = vendor.id
            updated += 1
        else:
            db.add(
                PurchaseOrder(
                    external_ref=ext.external_ref,
                    total=ext.total,
                    status=_map_status(ext.status),
                    vendor_id=vendor.id if vendor else None,
                )
            )
            created += 1
    await db.commit()
    return SyncResult(pulled=len(external), created=created, updated=updated)


@router.get("/reconciliation", response_model=ReconciliationResult)
async def reconciliation(db: AsyncSession = Depends(get_db)):
    invoices = erp.get_connector().fetch_invoices()
    pos, _ = await PurchaseOrderRepository(db).list_purchase_orders(limit=1000)
    return erp.reconcile(invoices, pos)
