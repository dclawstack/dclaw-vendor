import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.core.utils import utc_now
from app.repositories.performance_repo import PerformanceRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.performance import (
    BenchmarkResult,
    PerformanceScoreList,
    PerformanceScoreRead,
    ScoreRequest,
    TrendPoint,
)
from app.services import performance as perf
from app.services.llm import LLMError, LLMService

router = APIRouter()


async def _vendor_or_404(db: AsyncSession, vendor_id: uuid.UUID):
    vendor = await VendorRepository(db).get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.post("/vendors/{vendor_id}/score", response_model=PerformanceScoreRead)
async def score_vendor(
    vendor_id: uuid.UUID,
    payload: ScoreRequest | None = None,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    vendor = await _vendor_or_404(db, vendor_id)
    now = utc_now()
    period = (payload.period if payload else None) or perf.current_quarter(
        now.year, now.month
    )
    try:
        score = await perf.score_vendor(
            llm, vendor, list(vendor.purchase_orders), period
        )
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    db.add(score)
    await db.commit()
    await db.refresh(score)
    return score


@router.get("/vendors/{vendor_id}/scores", response_model=PerformanceScoreList)
async def list_scores(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _vendor_or_404(db, vendor_id)
    items = await PerformanceRepository(db).list_for_vendor(vendor_id)
    return PerformanceScoreList(items=items, total=len(items))


@router.get("/vendors/{vendor_id}/latest", response_model=PerformanceScoreRead)
async def latest_score(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    score = await PerformanceRepository(db).latest_for_vendor(vendor_id)
    if score is None:
        raise HTTPException(status_code=404, detail="No performance scores yet")
    return score


@router.get("/vendors/{vendor_id}/trend", response_model=list[TrendPoint])
async def trend(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    await _vendor_or_404(db, vendor_id)
    scores = await PerformanceRepository(db).list_for_vendor(vendor_id)
    # oldest → newest for charting
    return [
        TrendPoint(
            period=s.period, overall_score=s.overall_score, created_at=s.created_at
        )
        for s in reversed(scores)
    ]


@router.get("/vendors/{vendor_id}/benchmark", response_model=BenchmarkResult)
async def benchmark(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    vendor = await _vendor_or_404(db, vendor_id)
    overall, peer_count, peer_avg, percentile = await PerformanceRepository(
        db
    ).benchmark(vendor_id, vendor.category)
    peer_group = f"category:{vendor.category}" if vendor.category else "all vendors"
    return BenchmarkResult(
        vendor_id=vendor_id,
        vendor_overall=overall,
        peer_group=peer_group,
        peer_count=peer_count,
        peer_average=peer_avg,
        percentile=percentile,
    )
