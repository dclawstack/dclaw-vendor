import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.po_line_item import POLineItem
from app.repositories.po_line_item_repo import POLineItemRepository
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.schemas.po_line_item import (
    POLineItemCreate,
    POLineItemList,
    POLineItemRead,
    POLineItemUpdate,
)

router = APIRouter()


async def _recompute_po_total(db: AsyncSession, po_id: uuid.UUID) -> None:
    po_repo = PurchaseOrderRepository(db)
    po = await po_repo.get_by_id(po_id)
    if po is not None:
        await po_repo.recompute_total(po)


@router.get("", response_model=POLineItemList)
async def list_line_items(
    po_id: uuid.UUID | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    repo = POLineItemRepository(db)
    items, total = await repo.list_line_items(po_id, limit, offset)
    return POLineItemList(items=items, total=total)


@router.post("", response_model=POLineItemRead, status_code=status.HTTP_201_CREATED)
async def create_line_item(
    payload: POLineItemCreate, db: AsyncSession = Depends(get_db)
):
    po = await PurchaseOrderRepository(db).get_by_id(payload.po_id)
    if po is None:
        raise HTTPException(status_code=400, detail="po_id does not exist")
    repo = POLineItemRepository(db)
    item = await repo.create(POLineItem(**payload.model_dump()))
    await _recompute_po_total(db, item.po_id)
    return item


@router.patch("/{item_id}", response_model=POLineItemRead)
async def update_line_item(
    item_id: uuid.UUID,
    payload: POLineItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    repo = POLineItemRepository(db)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Line item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item = await repo.update(item)
    await _recompute_po_total(db, item.po_id)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_line_item(item_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    repo = POLineItemRepository(db)
    item = await repo.get_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Line item not found")
    po_id = item.po_id
    await repo.delete(item)
    await _recompute_po_total(db, po_id)
