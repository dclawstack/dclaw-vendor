from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.analytics import SpendInsights, SpendSummary
from app.services import analytics
from app.services.llm import LLMError, LLMService

router = APIRouter()


async def _load(db: AsyncSession):
    vendors, _ = await VendorRepository(db).list_vendors(limit=1000)
    pos, _ = await PurchaseOrderRepository(db).list_purchase_orders(limit=1000)
    return vendors, pos


@router.get("/spend", response_model=SpendSummary)
async def spend_summary(db: AsyncSession = Depends(get_db)):
    vendors, pos = await _load(db)
    return analytics.build_summary(vendors, pos)


@router.post("/spend/insights", response_model=SpendInsights)
async def spend_insights(
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    vendors, pos = await _load(db)
    summary = analytics.build_summary(vendors, pos)
    try:
        return await analytics.generate_insights(llm, summary)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
