import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import POStatus
from app.models.po_line_item import POLineItem
from app.models.purchase_order import PurchaseOrder
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.purchase_order import (
    PurchaseOrderCreate,
    PurchaseOrderList,
    PurchaseOrderRead,
    PurchaseOrderUpdate,
)

router = APIRouter()


@router.get("", response_model=PurchaseOrderList)
async def list_purchase_orders(
    vendor_id: uuid.UUID | None = None,
    status: POStatus | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = PurchaseOrderRepository(db)
    items, total = await repo.list_purchase_orders(vendor_id, status, limit, offset)
    return PurchaseOrderList(items=items, total=total)


@router.post("", response_model=PurchaseOrderRead, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    payload: PurchaseOrderCreate, db: AsyncSession = Depends(get_db)
):
    repo = PurchaseOrderRepository(db)
    if payload.vendor_id is not None:
        vendor = await VendorRepository(db).get_by_id(payload.vendor_id)
        if vendor is None:
            raise HTTPException(status_code=400, detail="vendor_id does not exist")

    po = PurchaseOrder(
        vendor_id=payload.vendor_id,
        status=payload.status,
        expected_delivery=payload.expected_delivery,
        notes=payload.notes,
        line_items=[POLineItem(**li.model_dump()) for li in payload.line_items],
    )
    po.total = repo.compute_total(po)
    return await repo.create(po)


@router.get("/{po_id}", response_model=PurchaseOrderRead)
async def get_purchase_order(po_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    return po


@router.patch("/{po_id}", response_model=PurchaseOrderRead)
async def update_purchase_order(
    po_id: uuid.UUID,
    payload: PurchaseOrderUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    data = payload.model_dump(exclude_unset=True)
    if "vendor_id" in data and data["vendor_id"] is not None:
        vendor = await VendorRepository(db).get_by_id(data["vendor_id"])
        if vendor is None:
            raise HTTPException(status_code=400, detail="vendor_id does not exist")
    for field, value in data.items():
        setattr(po, field, value)
    return await repo.update(po)


@router.delete("/{po_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_order(po_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(po_id)
    if po is None:
        raise HTTPException(status_code=404, detail="Purchase order not found")
    await repo.delete(po)
