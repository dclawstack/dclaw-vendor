import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sustainability import SustainabilityScore
from app.repositories.base_repo import BaseRepository


class SustainabilityRepository(BaseRepository[SustainabilityScore]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, SustainabilityScore)

    async def list_for_vendor(
        self, vendor_id: uuid.UUID, limit: int = 50
    ) -> list[SustainabilityScore]:
        stmt = (
            select(SustainabilityScore)
            .where(SustainabilityScore.vendor_id == vendor_id)
            .order_by(SustainabilityScore.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def latest_for_vendor(
        self, vendor_id: uuid.UUID
    ) -> SustainabilityScore | None:
        stmt = (
            select(SustainabilityScore)
            .where(SustainabilityScore.vendor_id == vendor_id)
            .order_by(SustainabilityScore.created_at.desc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
