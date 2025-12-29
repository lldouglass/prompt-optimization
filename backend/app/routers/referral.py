"""Router for referral program endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..auth import get_current_org_dual
from ..models import Organization, Referral, User
from ..schemas.referral import ReferralInfo, ReferralHistoryItem, ReferralHistoryResponse

router = APIRouter(prefix="/api/v1/referral", tags=["referral"])


def mask_email(email: str) -> str:
    """Mask email for privacy: john@example.com -> j***@example.com"""
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        return f"*@{domain}"
    return f"{local[0]}***@{domain}"


@router.get("/info", response_model=ReferralInfo)
async def get_referral_info(
    org: Organization = Depends(get_current_org_dual),
) -> ReferralInfo:
    """Get current user's referral code and stats."""
    return ReferralInfo(
        referral_code=org.referral_code or "",
        referral_link=f"https://app.clarynt.net/login?ref={org.referral_code}" if org.referral_code else "",
        total_referrals=org.total_referrals,
        bonus_optimizations_earned=org.bonus_optimizations,
    )


@router.get("/history", response_model=ReferralHistoryResponse)
async def get_referral_history(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> ReferralHistoryResponse:
    """Get list of users referred by this organization."""
    result = await db.execute(
        select(Referral)
        .where(Referral.referrer_org_id == org.id)
        .options(selectinload(Referral.referred_user))
        .order_by(Referral.created_at.desc())
        .limit(50)
    )
    referrals = result.scalars().all()

    items = [
        ReferralHistoryItem(
            referred_email=mask_email(r.referred_user.email),
            created_at=r.created_at,
            reward_given=r.referrer_reward,
        )
        for r in referrals
    ]

    return ReferralHistoryResponse(
        referrals=items,
        total=org.total_referrals,
    )
