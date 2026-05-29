import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_llm
from app.core.database import get_db
from app.core.utils import utc_now
from app.models.contract import Contract
from app.models.enums import ContractStatus
from app.repositories.contract_repo import ContractRepository
from app.repositories.vendor_repo import VendorRepository
from app.schemas.contract import (
    ContractCreate,
    ContractList,
    ContractRead,
    ContractUpdate,
    ExtractRequest,
    RenewalItem,
)
from app.services import contracts as contract_service
from app.services.llm import LLMError, LLMService

router = APIRouter()


async def _get_contract(db: AsyncSession, contract_id: uuid.UUID) -> Contract:
    c = await ContractRepository(db).get_by_id(contract_id)
    if c is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return c


@router.post("", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
async def create_contract(payload: ContractCreate, db: AsyncSession = Depends(get_db)):
    if await VendorRepository(db).get_by_id(payload.vendor_id) is None:
        raise HTTPException(status_code=404, detail="Vendor not found")
    contract = Contract(**payload.model_dump())
    contract.status = contract_service.derive_status(contract, utc_now().date())
    repo = ContractRepository(db)
    return await repo.create(contract)


@router.get("", response_model=ContractList)
async def list_contracts(
    vendor_id: uuid.UUID | None = None,
    status: ContractStatus | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await ContractRepository(db).list_contracts(
        vendor_id, status, limit, offset
    )
    return ContractList(items=items, total=total)


@router.get("/renewals", response_model=list[RenewalItem])
async def renewals(db: AsyncSession = Depends(get_db)):
    today = utc_now().date()
    items = await ContractRepository(db).renewals()
    return [
        RenewalItem(
            contract_id=c.id,
            vendor_id=c.vendor_id,
            title=c.title,
            end_date=c.end_date,
            days_to_expiry=contract_service.days_to_expiry(c, today),
            auto_renew=c.auto_renew,
            status=contract_service.derive_status(c, today),
        )
        for c in items
    ]


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract(contract_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await _get_contract(db, contract_id)


@router.patch("/{contract_id}", response_model=ContractRead)
async def update_contract(
    contract_id: uuid.UUID,
    payload: ContractUpdate,
    db: AsyncSession = Depends(get_db),
):
    contract = await _get_contract(db, contract_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(contract, field, value)
    # If the caller didn't set status explicitly, keep it in sync with the dates.
    if "status" not in data:
        contract.status = contract_service.derive_status(contract, utc_now().date())
    return await ContractRepository(db).update(contract)


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    contract = await _get_contract(db, contract_id)
    await ContractRepository(db).delete(contract)


@router.post("/{contract_id}/extract", response_model=ContractRead)
async def extract_terms(
    contract_id: uuid.UUID,
    payload: ExtractRequest,
    db: AsyncSession = Depends(get_db),
    llm: LLMService = Depends(get_llm),
):
    contract = await _get_contract(db, contract_id)
    try:
        terms = await contract_service.extract_terms(llm, payload.text)
    except LLMError as e:
        raise HTTPException(status_code=502, detail=f"LLM unavailable: {e}") from e
    contract.key_terms = terms.model_dump()
    return await ContractRepository(db).update(contract)
