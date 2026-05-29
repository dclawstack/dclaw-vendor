from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import VendorStatus, VendorTier
from app.models.vendor import Vendor
from app.repositories.base_repo import BaseRepository


class VendorRepository(BaseRepository[Vendor]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Vendor)

    async def list_vendors(
        self,
        search: str | None = None,
        status: VendorStatus | None = None,
        category: str | None = None,
        tier: VendorTier | None = None,
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
        if category:
            stmt = stmt.where(Vendor.category == category)
        if tier is not None:
            stmt = stmt.where(Vendor.tier == tier)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar() or 0

        stmt = stmt.order_by(Vendor.created_at.desc()).limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def _facet(self, column) -> list[tuple[str, int]]:
        stmt = (
            select(column, func.count())
            .where(column.is_not(None))
            .group_by(column)
            .order_by(func.count().desc())
        )
        rows = (await self.db.execute(stmt)).all()
        # enum columns come back as the enum member — normalise to its value
        return [(getattr(v, "value", v), c) for v, c in rows]

    async def facet_counts(self) -> dict[str, list[tuple[str, int]]]:
        """Counts grouped by status / category / tier / industry for directory facets."""
        return {
            "status": await self._facet(Vendor.status),
            "category": await self._facet(Vendor.category),
            "tier": await self._facet(Vendor.tier),
            "industry": await self._facet(Vendor.industry),
        }
