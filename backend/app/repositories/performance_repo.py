import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.performance import PerformanceScore
from app.models.vendor import Vendor
from app.repositories.base_repo import BaseRepository


class PerformanceRepository(BaseRepository[PerformanceScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, PerformanceScore)

    async def list_for_vendor(
        self, vendor_id: uuid.UUID, limit: int = 50
    ) -> list[PerformanceScore]:
        stmt = (
            select(PerformanceScore)
            .where(PerformanceScore.vendor_id == vendor_id)
            .order_by(PerformanceScore.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def latest_for_vendor(self, vendor_id: uuid.UUID) -> PerformanceScore | None:
        stmt = (
            select(PerformanceScore)
            .where(PerformanceScore.vendor_id == vendor_id)
            .order_by(PerformanceScore.created_at.desc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def _latest_overall_subquery(self):
        """Subquery: each vendor's most recent overall_score (via DISTINCT ON)."""
        return (
            select(
                PerformanceScore.vendor_id,
                PerformanceScore.overall_score,
            )
            .distinct(PerformanceScore.vendor_id)
            .order_by(
                PerformanceScore.vendor_id, PerformanceScore.created_at.desc()
            )
            .subquery()
        )

    async def benchmark(
        self, vendor_id: uuid.UUID, category: str | None
    ) -> tuple[float | None, int, float | None, float | None]:
        """Return (vendor_overall, peer_count, peer_average, percentile).

        Peers = latest score of every vendor (optionally filtered to the same
        category). Percentile = share of peers the vendor scores at-or-above.
        """
        latest = await self._latest_overall_subquery()

        stmt = select(latest.c.vendor_id, latest.c.overall_score)
        if category:
            stmt = stmt.join(Vendor, Vendor.id == latest.c.vendor_id).where(
                Vendor.category == category
            )
        rows = (await self.db.execute(stmt)).all()
        scores = {vid: score for vid, score in rows}

        vendor_overall = scores.get(vendor_id)
        peer_scores = [s for vid, s in scores.items() if vid != vendor_id]
        peer_count = len(peer_scores)
        peer_average = round(sum(peer_scores) / peer_count, 1) if peer_count else None

        percentile = None
        if vendor_overall is not None and peer_count:
            at_or_below = sum(1 for s in peer_scores if s <= vendor_overall)
            percentile = round(100 * at_or_below / peer_count, 1)
        return vendor_overall, peer_count, peer_average, percentile
