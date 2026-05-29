import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import POStatus
from app.models.po_line_item import POLineItem
from app.models.purchase_order import PurchaseOrder
from app.repositories.base_repo import BaseRepository


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, PurchaseOrder)

    async def list_purchase_orders(
        self,
        vendor_id: uuid.UUID | None = None,
        status: POStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[PurchaseOrder], int]:
        stmt = select(PurchaseOrder)
        if vendor_id is not None:
            stmt = stmt.where(PurchaseOrder.vendor_id == vendor_id)
        if status is not None:
            stmt = stmt.where(PurchaseOrder.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = (
            stmt.order_by(PurchaseOrder.created_at.desc()).limit(limit).offset(offset)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    @staticmethod
    def compute_total(po: PurchaseOrder) -> float:
        """Total from an in-memory PO's loaded line items (used at create time)."""
        return round(
            sum(li.quantity * li.unit_price for li in po.line_items), 2
        )

    async def recompute_total(self, po: PurchaseOrder) -> PurchaseOrder:
        """Recompute and persist a PO total via a SQL aggregate over its line
        items — avoids stale identity-mapped collections after mutations."""
        result = await self.db.execute(
            select(
                func.coalesce(func.sum(POLineItem.quantity * POLineItem.unit_price), 0.0)
            ).where(POLineItem.po_id == po.id)
        )
        po.total = round(float(result.scalar() or 0.0), 2)
        await self.db.commit()
        await self.db.refresh(po)
        return po
