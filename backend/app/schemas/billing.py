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
    tokens_used_this_month: int = 0
    estimated_cost_cents: int = 0  # Cost in cents (e.g., 23 = $0.23)
    usage_reset_at: datetime | None = None
    # Referral bonuses
    bonus_optimizations: int = 0  # Extra optimizations from referrals
    total_referrals: int = 0  # Count of successful referrals


class BillingInfo(BaseModel):
    subscription: SubscriptionInfo
    usage: UsageInfo


class CreateCheckoutRequest(BaseModel):
    plan: str  # 'pro' or 'team'
    billing_period: str = "monthly"  # 'monthly' or 'yearly'


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
    "team": {  # Premium plan ($15/mo) - uses "team" internally for Stripe mapping
        "requests_per_month": 25000,
        "optimizations_per_month": 200,
        "data_retention_days": 30,
        "team_members": 3,
    },
    "pro": {  # Pro plan ($90/mo)
        "requests_per_month": 100000,
        "optimizations_per_month": -1,  # unlimited
        "data_retention_days": 90,
        "team_members": 10,
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
