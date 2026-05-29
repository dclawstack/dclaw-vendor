"""Billing (Stripe, V8.2).

A ``BillingProvider`` abstraction with two backends:

- **MockBilling** (default) — returns a deterministic per-seat plan, a fake active
  subscription, and a fake checkout URL, so the billing UI/API are exercisable in
  dev/CI with no Stripe account.
- **StripeBilling** — talks to the Stripe REST API over httpx (no extra SDK dep);
  activates when ``BILLING_BACKEND=stripe`` and ``STRIPE_API_KEY`` is set. Creates a
  per-seat Checkout Session and reads the current subscription.

``get_billing()`` resolves the configured backend.
"""

from __future__ import annotations

from typing import Protocol

import httpx

from app.core.config import settings
from app.schemas.billing import CheckoutSession, Plan, Subscription

PLANS = [
    Plan(id="starter", name="Starter", price_per_seat=0.0, features=["Up to 25 vendors", "Copilot"]),
    Plan(id="growth", name="Growth", price_per_seat=49.0, features=["Unlimited vendors", "AI scoring", "Analytics"]),
    Plan(id="enterprise", name="Enterprise", price_per_seat=99.0, features=["SSO", "Audit log", "Priority support"]),
]


class BillingProvider(Protocol):
    def plans(self) -> list[Plan]: ...
    def subscription(self) -> Subscription: ...
    def create_checkout(self, plan_id: str, seats: int) -> CheckoutSession: ...


class MockBilling:
    def plans(self) -> list[Plan]:
        return PLANS

    def subscription(self) -> Subscription:
        return Subscription(plan_id="growth", plan_name="Growth", seats=5, status="active", backend="mock")

    def create_checkout(self, plan_id: str, seats: int) -> CheckoutSession:
        return CheckoutSession(url=f"{settings.billing_success_url}&plan={plan_id}&seats={seats}", backend="mock")


class StripeBilling:
    BASE = "https://api.stripe.com/v1"

    def __init__(self):
        self.headers = {"Authorization": f"Bearer {settings.stripe_api_key}"}

    def plans(self) -> list[Plan]:
        return PLANS

    def subscription(self) -> Subscription:
        with httpx.Client(timeout=15.0, headers=self.headers) as client:
            resp = client.get(f"{self.BASE}/subscriptions", params={"limit": 1})
            resp.raise_for_status()
            data = resp.json().get("data", [])
        if not data:
            return Subscription(plan_id="starter", plan_name="Starter", seats=0, status="none", backend="stripe")
        sub = data[0]
        item = (sub.get("items", {}).get("data") or [{}])[0]
        return Subscription(
            plan_id=item.get("price", {}).get("id", "unknown"),
            plan_name=sub.get("status", "active").title(),
            seats=item.get("quantity", 1),
            status=sub.get("status", "active"),
            backend="stripe",
        )

    def create_checkout(self, plan_id: str, seats: int) -> CheckoutSession:
        form = {
            "mode": "subscription",
            "line_items[0][price]": settings.stripe_price_id or plan_id,
            "line_items[0][quantity]": str(seats),
            "success_url": settings.billing_success_url,
            "cancel_url": settings.billing_cancel_url,
        }
        with httpx.Client(timeout=15.0, headers=self.headers) as client:
            resp = client.post(f"{self.BASE}/checkout/sessions", data=form)
            resp.raise_for_status()
            url = resp.json().get("url", "")
        return CheckoutSession(url=url, backend="stripe")


def get_billing() -> BillingProvider:
    if settings.billing_backend == "stripe" and settings.stripe_api_key:
        return StripeBilling()
    return MockBilling()
