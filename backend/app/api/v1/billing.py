from fastapi import APIRouter, HTTPException

from app.schemas.billing import (
    CheckoutRequest,
    CheckoutSession,
    Plan,
    Subscription,
)
from app.services import billing

router = APIRouter()


@router.get("/plans", response_model=list[Plan])
async def plans():
    return billing.get_billing().plans()


@router.get("/subscription", response_model=Subscription)
async def subscription():
    return billing.get_billing().subscription()


@router.post("/checkout", response_model=CheckoutSession)
async def checkout(payload: CheckoutRequest):
    valid = {p.id for p in billing.get_billing().plans()}
    if payload.plan_id not in valid:
        raise HTTPException(status_code=400, detail="Unknown plan")
    return billing.get_billing().create_checkout(payload.plan_id, payload.seats)
