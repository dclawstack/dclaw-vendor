import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.risk import RiskAssessment
from app.repositories.base_repo import BaseRepository


class RiskRepository(BaseRepository[RiskAssessment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, RiskAssessment)

    async def list_for_vendor(
        self, vendor_id: uuid.UUID, limit: int = 50
    ) -> list[RiskAssessment]:
        stmt = (
            select(RiskAssessment)
            .where(RiskAssessment.vendor_id == vendor_id)
            .order_by(RiskAssessment.created_at.desc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def latest_for_vendor(self, vendor_id: uuid.UUID) -> RiskAssessment | None:
        stmt = (
            select(RiskAssessment)
            .where(RiskAssessment.vendor_id == vendor_id)
            .order_by(RiskAssessment.created_at.desc())
            .limit(1)
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()
