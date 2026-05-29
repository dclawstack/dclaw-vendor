import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.vendor_repo import VendorRepository
from app.schemas.copilot import ChatRequest, CopilotReply
from app.schemas.evaluation import BatchEvaluationResponse, VendorEvaluationResult
from app.services import settings_service
from app.services.copilot_chat import run_chat
from app.services.llm import LLMError, LLMService
from app.services.retrieval import build_copilot_context
from app.services.vendor_evaluation import evaluate_batch, evaluate_vendor

router = APIRouter()


async def get_llm(db: AsyncSession = Depends(get_db)) -> LLMService:
    """Resolve the configured LLM provider into a service instance."""
    row = await settings_service.get_settings_row(db)
    return LLMService(settings_service.to_config(row))


@router.post("/chat", response_model=CopilotReply)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    last_user = next(
        (m.content for m in reversed(request.messages) if m.role == "user"), None
    )
    context = await build_copilot_context(
        db, vendor_id=request.vendor_id, query=last_user
    )
    try:
        return await run_chat(llm, context, request.messages)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e


@router.post("/vendors/{vendor_id}/evaluate", response_model=VendorEvaluationResult)
async def evaluate_one(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    vendor = await VendorRepository(db).get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    try:
        evaluation = await evaluate_vendor(llm, vendor, list(vendor.purchase_orders))
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    return VendorEvaluationResult(
        vendor_id=vendor.id, vendor_name=vendor.name, evaluation=evaluation
    )


@router.post("/vendors/evaluate-batch", response_model=BatchEvaluationResponse)
async def evaluate_batch_endpoint(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    vendors, _ = await VendorRepository(db).list_vendors(limit=limit)
    pairs = [(v, list(v.purchase_orders)) for v in vendors]
    results = await evaluate_batch(llm, pairs)
    failed = sum(1 for r in results if r.error)
    return BatchEvaluationResponse(
        results=results, evaluated=len(results) - failed, failed=failed
    )
