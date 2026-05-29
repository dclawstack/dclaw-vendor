import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.models.risk import RiskAssessment
from app.repositories.risk_repo import RiskRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.risk import (
    RiskAssessmentList,
    RiskAssessmentRead,
    RiskMonitorResult,
)
from app.services import risk as risk_service
from app.services.llm import LLMError, LLMService

router = APIRouter()


async def _vendor_or_404(db: AsyncSession, vendor_id: uuid.UUID):
    vendor = await VendorRepository(db).get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.get("/types", response_model=list[str])
async def risk_types():
    return risk_service.RISK_TYPES


@router.post("/vendors/{vendor_id}/assess", response_model=RiskMonitorResult)
async def assess(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    vendor = await _vendor_or_404(db, vendor_id)
    repo = RiskRepository(db)
    previous = await repo.latest_for_vendor(vendor_id)
    try:
        analysis = await risk_service.assess_vendor(
            llm, vendor, list(vendor.purchase_orders)
        )
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e

    factors = [f.model_dump() for f in analysis.factors]
    changes = risk_service.diff_factors(
        previous.factors if previous else None, factors
    )
    assessment = RiskAssessment(
        vendor_id=vendor_id,
        overall_level=analysis.overall_level,
        overall_score=analysis.overall_score,
        factors=factors,
        summary=analysis.summary,
    )
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    return RiskMonitorResult(
        assessment=RiskAssessmentRead.model_validate(assessment), changes=changes
    )


@router.get("/vendors/{vendor_id}/latest", response_model=RiskAssessmentRead)
async def latest(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    assessment = await RiskRepository(db).latest_for_vendor(vendor_id)
    if assessment is None:
        raise HTTPException(status_code=404, detail="No risk assessment yet")
    return assessment


@router.get("/vendors/{vendor_id}/history", response_model=RiskAssessmentList)
async def history(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _vendor_or_404(db, vendor_id)
    items = await RiskRepository(db).list_for_vendor(vendor_id)
    return RiskAssessmentList(items=items, total=len(items))
