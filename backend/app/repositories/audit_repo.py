import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import Audit
from app.models.enums import AuditStatus
from app.repositories.base_repo import BaseRepository


class AuditRepository(BaseRepository[Audit]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Audit)

    async def list_audits(
        self,
        vendor_id: uuid.UUID | None = None,
        status: AuditStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Audit], int]:
        stmt = select(Audit)
        if vendor_id is not None:
            stmt = stmt.where(Audit.vendor_id == vendor_id)
        if status is not None:
            stmt = stmt.where(Audit.status == status)
        total = (
            await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar() or 0
        stmt = stmt.order_by(Audit.created_at.desc()).limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total
