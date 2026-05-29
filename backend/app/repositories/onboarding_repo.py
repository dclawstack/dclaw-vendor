import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OnboardingStatus
from app.models.onboarding import OnboardingCase
from app.repositories.base_repo import BaseRepository


class OnboardingRepository(BaseRepository[OnboardingCase]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, OnboardingCase)

    async def list_cases(
        self,
        vendor_id: uuid.UUID | None = None,
        status: OnboardingStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[OnboardingCase], int]:
        stmt = select(OnboardingCase)
        if vendor_id is not None:
            stmt = stmt.where(OnboardingCase.vendor_id == vendor_id)
        if status is not None:
            stmt = stmt.where(OnboardingCase.status == status)

        total = (
            await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar() or 0
        stmt = (
            stmt.order_by(OnboardingCase.created_at.desc()).limit(limit).offset(offset)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total
