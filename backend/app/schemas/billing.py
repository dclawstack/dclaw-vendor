"""Schemas for billing (Stripe, V8.2)."""

from pydantic import BaseModel, Field


class Plan(BaseModel):
    id: str
    name: str
    price_per_seat: float
    features: list[str]


class Subscription(BaseModel):
    plan_id: str
    plan_name: str
    seats: int
    status: str
    backend: str


class CheckoutRequest(BaseModel):
    plan_id: str
    seats: int = Field(default=1, ge=1)


class CheckoutSession(BaseModel):
    url: str
    backend: str
