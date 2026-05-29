import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import VendorStatus
from app.models.vendor import Vendor
from app.repositories.vendor_repo import VendorRepository
from app.schemas.vendor import VendorCreate, VendorList, VendorRead, VendorUpdate

router = APIRouter()


@router.get("", response_model=VendorList)
async def list_vendors(
    search: str | None = None,
    status: VendorStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = VendorRepository(db)
    items, total = await repo.list_vendors(search, status, limit, offset)
    return VendorList(items=items, total=total)


@router.post("", response_model=VendorRead, status_code=status.HTTP_201_CREATED)
async def create_vendor(payload: VendorCreate, db: AsyncSession = Depends(get_db)):
    repo = VendorRepository(db)
    vendor = Vendor(**payload.model_dump())
    return await repo.create(vendor)


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
