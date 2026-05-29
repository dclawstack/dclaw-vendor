import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.core.utils import utc_now
from app.repositories.sustainability_repo import SustainabilityRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.sustainability import (
    ScoreRequest,
    SustainabilityScoreList,
    SustainabilityScoreRead,
)
from app.services import sustainability as sus
from app.services.llm import LLMError, LLMService
from app.services.performance import current_quarter

router = APIRouter()


async def _vendor_or_404(db: AsyncSession, vendor_id: uuid.UUID):
    vendor = await VendorRepository(db).get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.post("/vendors/{vendor_id}/score", response_model=SustainabilityScoreRead)
async def score(
    vendor_id: uuid.UUID,
    payload: ScoreRequest | None = None,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    vendor = await _vendor_or_404(db, vendor_id)
    now = utc_now()
    period = (payload.period if payload else None) or current_quarter(now.year, now.month)
    try:
        score = await sus.score_vendor(llm, vendor, list(vendor.purchase_orders), period)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return score


@router.get("/vendors/{vendor_id}/latest", response_model=SustainabilityScoreRead)
async def latest(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    score = await SustainabilityRepository(db).latest_for_vendor(vendor_id)
    if score is None:
        raise HTTPException(status_code=404, detail="No sustainability score yet")
    return score


@router.get("/vendors/{vendor_id}/history", response_model=SustainabilityScoreList)
async def history(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _vendor_or_404(db, vendor_id)
    items = await SustainabilityRepository(db).list_for_vendor(vendor_id)
    return SustainabilityScoreList(items=items, total=len(items))
