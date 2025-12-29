from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models.organization import Organization
from .schemas.billing import get_plan_limits


async def check_and_increment_usage(
    org_id: str,
    db: AsyncSession,
    usage_type: str = "requests"  # "requests" or "optimizations"
) -> None:
    """
    Check if the organization is within their usage limits and increment the counter.
    Raises HTTPException if limit exceeded.

    Args:
        org_id: The organization ID
        db: Database session
        usage_type: Either "requests" or "optimizations"
    """
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Check if we need to reset usage (monthly reset)
    now = datetime.utcnow()
    if org.usage_reset_at is None or now >= org.usage_reset_at:
        # Reset usage counters
        org.requests_this_month = 0
        org.optimizations_this_month = 0
        # Set next reset to first of next month
        next_month = now.replace(day=1) + timedelta(days=32)
        org.usage_reset_at = next_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Get plan limits
    limits = get_plan_limits(org.subscription_plan)

    # Check limits based on usage type
    if usage_type == "requests":
        limit = limits["requests_per_month"]
        current = org.requests_this_month
        if limit != -1 and current >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Request limit exceeded. Your {org.subscription_plan} plan allows {limit:,} requests/month. Upgrade your plan for more."
            )
        org.requests_this_month += 1

    elif usage_type == "optimizations":
        base_limit = limits["optimizations_per_month"]
        # Add bonus optimizations from referrals to the limit
        effective_limit = base_limit + org.bonus_optimizations if base_limit != -1 else -1
        current = org.optimizations_this_month
        if effective_limit != -1 and current >= effective_limit:
            bonus_msg = f" (+{org.bonus_optimizations} bonus)" if org.bonus_optimizations > 0 else ""
            raise HTTPException(
                status_code=429,
                detail=f"Optimization limit exceeded. Your {org.subscription_plan} plan allows {base_limit:,}{bonus_msg} optimizations/month. Refer friends for more!"
            )
        org.optimizations_this_month += 1

    await db.commit()


async def get_usage_stats(org_id: str, db: AsyncSession) -> dict:
    """Get current usage statistics for an organization."""
    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        return {}

    limits = get_plan_limits(org.subscription_plan)

    base_opt_limit = limits["optimizations_per_month"]
    effective_opt_limit = base_opt_limit + org.bonus_optimizations if base_opt_limit != -1 else -1

    return {
        "requests": {
            "used": org.requests_this_month,
            "limit": limits["requests_per_month"],
        },
        "optimizations": {
            "used": org.optimizations_this_month,
            "limit": effective_opt_limit,
            "base_limit": base_opt_limit,
            "bonus": org.bonus_optimizations,
        },
        "reset_at": org.usage_reset_at.isoformat() if org.usage_reset_at else None,
        "total_referrals": org.total_referrals,
    }
