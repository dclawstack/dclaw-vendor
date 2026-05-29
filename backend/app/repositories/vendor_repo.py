from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import VendorStatus
from app.models.vendor import Vendor
from app.repositories.base_repo import BaseRepository


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Vendor)

    async def list_vendors(
        self,
        search: str | None = None,
        status: VendorStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Vendor], int]:
        stmt = select(Vendor)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(Vendor.name.ilike(pattern), Vendor.email.ilike(pattern))
            )
        if status is not None:
            stmt = stmt.where(Vendor.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(Vendor.created_at.desc()).limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total
