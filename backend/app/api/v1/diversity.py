from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.purchase_order_repo import PurchaseOrderRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.diversity import DiversityReport
from app.services import diversity

router = APIRouter()


@router.get("/report", response_model=DiversityReport)
async def report(db: AsyncSession = Depends(get_db)):
    vendors, _ = await VendorRepository(db).list_vendors(limit=1000)
    pos, _ = await PurchaseOrderRepository(db).list_purchase_orders(limit=1000)
    return diversity.build_report(vendors, pos)
