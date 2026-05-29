import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.survey import Survey
from app.repositories.base_repo import BaseRepository


class SurveyRepository(BaseRepository[Survey]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Survey)

    async def list_surveys(
        self,
        vendor_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Survey], int]:
        stmt = select(Survey)
        if vendor_id is not None:
            stmt = stmt.where(Survey.vendor_id == vendor_id)
        total = (
            await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar() or 0
        stmt = stmt.order_by(Survey.created_at.desc()).limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def for_vendor(self, vendor_id: uuid.UUID) -> list[Survey]:
        stmt = select(Survey).where(Survey.vendor_id == vendor_id)
        return list((await self.db.execute(stmt)).scalars().all())
