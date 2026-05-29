import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.audit import Audit, AuditFinding
from app.models.enums import AuditStatus, FindingStatus
from app.repositories.audit_repo import AuditRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.audit import (
    AuditCreate,
    AuditFindingCreate,
    AuditFindingRead,
    AuditFindingUpdate,
    AuditList,
    AuditRead,
    AuditUpdate,
)
from app.services import audit as audit_service

router = APIRouter()


async def _get_audit(db: AsyncSession, audit_id: uuid.UUID) -> Audit:
    audit = await AuditRepository(db).get_by_id(audit_id)
    if audit is None:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.post("", response_model=AuditRead, status_code=status.HTTP_201_CREATED)
async def create_audit(payload: AuditCreate, db: AsyncSession = Depends(get_db)):
    if await VendorRepository(db).get_by_id(payload.vendor_id) is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    audit = Audit(**payload.model_dump())
    db.add(audit)
    await db.commit()
    await db.refresh(audit)
    return audit


@router.get("", response_model=AuditList)
async def list_audits(
    vendor_id: uuid.UUID | None = None,
    status: AuditStatus | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await AuditRepository(db).list_audits(vendor_id, status, limit, offset)
    return AuditList(items=items, total=total)


@router.get("/{audit_id}", response_model=AuditRead)
async def get_audit(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_audit(db, audit_id)


@router.patch("/{audit_id}", response_model=AuditRead)
async def update_audit(
    audit_id: uuid.UUID, payload: AuditUpdate, db: AsyncSession = Depends(get_db)
):
    audit = await _get_audit(db, audit_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(audit, field, value)
    await db.commit()
    await db.refresh(audit)
    return audit


@router.delete("/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    audit = await _get_audit(db, audit_id)
    await db.delete(audit)
    await db.commit()


@router.post("/{audit_id}/close", response_model=AuditRead)
async def close_audit(audit_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    audit = await _get_audit(db, audit_id)
    try:
        audit_service.close_audit(audit)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    await db.commit()
    await db.refresh(audit)
    return audit


# --- findings -----------------------------------------------------------


@router.post(
    "/{audit_id}/findings",
    response_model=AuditFindingRead,
    status_code=status.HTTP_201_CREATED,
)
async def add_finding(
    audit_id: uuid.UUID,
    payload: AuditFindingCreate,
    db: AsyncSession = Depends(get_db),
):
    await _get_audit(db, audit_id)
    finding = AuditFinding(audit_id=audit_id, **payload.model_dump())
    db.add(finding)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.patch("/findings/{finding_id}", response_model=AuditFindingRead)
async def update_finding(
    finding_id: uuid.UUID,
    payload: AuditFindingUpdate,
    db: AsyncSession = Depends(get_db),
):
    finding = await db.get(AuditFinding, finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    data = payload.model_dump(exclude_unset=True)
    # Closing a finding via status stamps closed_at.
    if data.get("status") == FindingStatus.closed and finding.status != FindingStatus.closed:
        audit_service.close_finding(finding)
        data.pop("status", None)
    for field, value in data.items():
        setattr(finding, field, value)
    await db.commit()
    await db.refresh(finding)
    return finding
