import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.models.enums import VendorStatus, VendorTier
from app.models.vendor import Vendor
from app.repositories.vendor_repo import VendorRepository
from app.schemas.classification import (
    BatchClassificationResponse,
    VendorClassificationResult,
)
from app.schemas.enrichment import VendorEnrichmentResult
from app.schemas.vendor import (
    FacetCount,
    VendorCreate,
    VendorFacets,
    VendorList,
    VendorRead,
    VendorUpdate,
)
from app.services.llm import LLMError, LLMService
from app.services.vendor_classification import classify_batch, classify_vendor
from app.services.vendor_enrichment import enrich_vendor

router = APIRouter()


@router.get("", response_model=VendorList)
async def list_vendors(
    search: str | None = None,
    status: VendorStatus | None = None,
    category: str | None = None,
    tier: VendorTier | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = VendorRepository(db)
    items, total = await repo.list_vendors(
        search, status, category, tier, limit, offset
    )
    return VendorList(items=items, total=total)


@router.get("/facets", response_model=VendorFacets)
async def vendor_facets(db: AsyncSession = Depends(get_db)):
    repo = VendorRepository(db)
    facets = await repo.facet_counts()
    total = await repo.count()
    return VendorFacets(
        status=[FacetCount(value=v, count=c) for v, c in facets["status"]],
        category=[FacetCount(value=v, count=c) for v, c in facets["category"]],
        tier=[FacetCount(value=v, count=c) for v, c in facets["tier"]],
        industry=[FacetCount(value=v, count=c) for v, c in facets["industry"]],
        total=total,
    )


@router.post("", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(payload: VendorCreate, db: AsyncSession = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = Vendor(**payload.model_dump())
    return await repo.create(vendor)


@router.post("/classify-batch", response_model=BatchClassificationResponse)
async def classify_batch_endpoint(
    limit: int = Query(100, ge=1, le=500),
    only_unclassified: bool = True,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    """Bulk-classify vendors and persist category/industry/tier (V3.1/V3.4)."""
    repo = VendorRepository(db)
    vendors, _ = await repo.list_vendors(limit=limit)
    if only_unclassified:
        vendors = [v for v in vendors if v.tier is None]
    results = await classify_batch(llm, vendors)
    by_id = {v.id: v for v in vendors}
    for r in results:
        if r.classification:
            v = by_id[r.vendor_id]
            v.category = r.classification.category
            v.industry = r.classification.industry
            v.tier = r.classification.tier
    await db.commit()
    failed = sum(1 for r in results if r.error)
    return BatchClassificationResponse(
        results=results, classified=len(results) - failed, failed=failed
    )


@router.get("/{vendor_id}", response_model=VendorRead)
async def get_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = await repo.get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.patch("/{vendor_id}", response_model=VendorRead)
async def update_vendor(
    vendor_id: uuid.UUID,
    payload: VendorUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = VendorRepository(db)
    vendor = await repo.get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(vendor, field, value)
    return await repo.update(vendor)


@router.delete("/{vendor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vendor(vendor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = await repo.get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    await repo.delete(vendor)


@router.post("/{vendor_id}/classify", response_model=VendorClassificationResult)
async def classify_one(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    repo = VendorRepository(db)
    vendor = await repo.get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    try:
        classification = await classify_vendor(llm, vendor)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    vendor.category = classification.category
    vendor.industry = classification.industry
    vendor.tier = classification.tier
    await repo.update(vendor)
    return VendorClassificationResult(
        vendor_id=vendor.id, vendor_name=vendor.name, classification=classification
    )


@router.post("/{vendor_id}/enrich", response_model=VendorEnrichmentResult)
async def enrich_one(
    vendor_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    repo = VendorRepository(db)
    vendor = await repo.get_by_id(vendor_id)
    if vendor is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    try:
        enrichment = await enrich_vendor(llm, vendor)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    vendor.enrichment = enrichment
    # adopt the enriched industry if we didn't have one
    if not vendor.industry and enrichment.get("industry"):
        vendor.industry = enrichment["industry"]
    await repo.update(vendor)
    return VendorEnrichmentResult(
        vendor_id=vendor.id, vendor_name=vendor.name, enrichment=enrichment
    )
