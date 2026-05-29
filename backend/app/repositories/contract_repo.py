import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract
from app.models.enums import ContractStatus
from app.repositories.base_repo import BaseRepository


class ContractRepository(BaseRepository[Contract]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Contract)

    async def list_contracts(
        self,
        vendor_id: uuid.UUID | None = None,
        status: ContractStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Contract], int]:
        stmt = select(Contract)
        if vendor_id is not None:
            stmt = stmt.where(Contract.vendor_id == vendor_id)
        if status is not None:
            stmt = stmt.where(Contract.status == status)
        total = (
            await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        ).scalar() or 0
        stmt = stmt.order_by(Contract.created_at.desc()).limit(limit).offset(offset)
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def renewals(self, limit: int = 100) -> list[Contract]:
        """Contracts with an end date, soonest first — caller computes days/flags."""
        stmt = (
            select(Contract)
            .where(Contract.end_date.is_not(None))
            .where(Contract.status != ContractStatus.terminated)
            .order_by(Contract.end_date.asc())
            .limit(limit)
        )
        return list((await self.db.execute(stmt)).scalars().all())
