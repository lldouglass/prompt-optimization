"""Referral program schemas."""

from datetime import datetime
from pydantic import BaseModel


class ReferralInfo(BaseModel):
    """Current user's referral information."""
    referral_code: str
    referral_link: str
    total_referrals: int
    bonus_optimizations_earned: int


class ReferralHistoryItem(BaseModel):
    """A single referral in the history list."""
    referred_email: str  # Masked email: j***@example.com
    created_at: datetime
    reward_given: int  # Optimizations given to referrer

    model_config = {"from_attributes": True}


class ReferralHistoryResponse(BaseModel):
    """List of referrals made by the user."""
    referrals: list[ReferralHistoryItem]
    total: int
