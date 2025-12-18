from pydantic import BaseModel
from datetime import datetime


class SubscriptionInfo(BaseModel):
    plan: str
    status: str
    period_end: datetime | None = None
    stripe_customer_id: str | None = None


class UsageInfo(BaseModel):
    requests_this_month: int
    optimizations_this_month: int
    requests_limit: int
    optimizations_limit: int
    usage_reset_at: datetime | None = None


class BillingInfo(BaseModel):
    subscription: SubscriptionInfo
    usage: UsageInfo


class CreateCheckoutRequest(BaseModel):
    plan: str  # 'pro' or 'team'


class CheckoutSessionResponse(BaseModel):
    checkout_url: str
    session_id: str


class PortalSessionResponse(BaseModel):
    portal_url: str


# Plan limits
PLAN_LIMITS = {
    "free": {
        "requests_per_month": 1000,
        "optimizations_per_month": 10,
        "data_retention_days": 7,
        "team_members": 1,
    },
    "pro": {
        "requests_per_month": 50000,
        "optimizations_per_month": 100,
        "data_retention_days": 90,
        "team_members": 5,
    },
    "team": {
        "requests_per_month": 500000,
        "optimizations_per_month": -1,  # unlimited
        "data_retention_days": 365,
        "team_members": -1,  # unlimited
    },
    "enterprise": {
        "requests_per_month": -1,  # unlimited
        "optimizations_per_month": -1,
        "data_retention_days": -1,  # unlimited
        "team_members": -1,
    },
}


def get_plan_limits(plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
