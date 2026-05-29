import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.po_line_item import POLineItem
from app.repositories.base_repo import BaseRepository


class POLineItemRepository(BaseRepository[POLineItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, POLineItem)

    async def list_line_items(
        self,
        po_id: uuid.UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[POLineItem], int]:
        stmt = select(POLineItem)
        if po_id is not None:
            stmt = stmt.where(POLineItem.po_id == po_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(POLineItem.created_at).limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total
