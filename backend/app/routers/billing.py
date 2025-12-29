import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..database import get_db
from ..auth import get_current_org_dual
from ..models.organization import Organization
from ..config import get_settings
from ..schemas.billing import (
    BillingInfo,
    SubscriptionInfo,
    UsageInfo,
    CreateCheckoutRequest,
    CheckoutSessionResponse,
    PortalSessionResponse,
    get_plan_limits,
)

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])
settings = get_settings()


def init_stripe():
    if settings.stripe_secret_key:
        stripe.api_key = settings.stripe_secret_key


def get_plan_from_price_id(price_id: str) -> str:
    """Determine plan from Stripe price ID (handles both monthly and yearly)."""
    if price_id in (settings.stripe_price_pro, settings.stripe_price_pro_yearly):
        return "pro"
    elif price_id in (settings.stripe_price_team, settings.stripe_price_team_yearly):
        return "team"
    return "free"


@router.get("", response_model=BillingInfo)
async def get_billing_info(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Get current billing and usage information."""
    limits = get_plan_limits(org.subscription_plan)
    base_opt_limit = limits["optimizations_per_month"]
    # Include bonus optimizations in the effective limit
    effective_opt_limit = base_opt_limit + org.bonus_optimizations if base_opt_limit != -1 else -1

    return BillingInfo(
        subscription=SubscriptionInfo(
            plan=org.subscription_plan,
            status=org.subscription_status,
            period_end=org.subscription_period_end,
            stripe_customer_id=org.stripe_customer_id,
        ),
        usage=UsageInfo(
            requests_this_month=org.requests_this_month,
            optimizations_this_month=org.optimizations_this_month,
            requests_limit=limits["requests_per_month"],
            optimizations_limit=effective_opt_limit,
            tokens_used_this_month=org.tokens_used_this_month,
            estimated_cost_cents=org.estimated_cost_cents,
            usage_reset_at=org.usage_reset_at,
            bonus_optimizations=org.bonus_optimizations,
            total_referrals=org.total_referrals,
        ),
    )


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for subscription."""
    init_stripe()

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    # Get price ID based on plan and billing period
    price_id = None
    is_yearly = request.billing_period == "yearly"

    if request.plan == "pro":
        price_id = settings.stripe_price_pro_yearly if is_yearly else settings.stripe_price_pro
    elif request.plan == "team":
        price_id = settings.stripe_price_team_yearly if is_yearly else settings.stripe_price_team
    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if not price_id:
        raise HTTPException(status_code=503, detail=f"Price for {request.plan} ({request.billing_period}) not configured")

    # Create or get Stripe customer
    if org.stripe_customer_id:
        customer_id = org.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            name=org.name,
            metadata={"organization_id": str(org.id)},
        )
        customer_id = customer.id
        org.stripe_customer_id = customer_id
        await db.commit()

    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[
            {
                "price": price_id,
                "quantity": 1,
            }
        ],
        mode="subscription",
        success_url=f"{settings.app_url}/settings?checkout=success",
        cancel_url=f"{settings.app_url}/settings?checkout=canceled",
        metadata={"organization_id": str(org.id)},
    )

    return CheckoutSessionResponse(
        checkout_url=session.url,
        session_id=session.id,
    )


@router.post("/portal", response_model=PortalSessionResponse)
async def create_portal_session(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe customer portal session for managing subscription."""
    init_stripe()

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    if not org.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account set up")

    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=f"{settings.app_url}/settings",
    )

    return PortalSessionResponse(portal_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events."""
    init_stripe()

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    payload = await request.body()

    # Verify webhook signature if secret is configured
    if settings.stripe_webhook_secret and stripe_signature:
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, settings.stripe_webhook_secret
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # For testing without webhook signature
        import json
        event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)

    # Handle the event
    if event.type == "checkout.session.completed":
        session = event.data.object
        await handle_checkout_completed(session, db)

    elif event.type == "customer.subscription.updated":
        subscription = event.data.object
        await handle_subscription_updated(subscription, db)

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object
        await handle_subscription_deleted(subscription, db)

    elif event.type == "invoice.payment_failed":
        invoice = event.data.object
        await handle_payment_failed(invoice, db)

    return {"status": "ok"}


async def handle_checkout_completed(session, db: AsyncSession):
    """Handle successful checkout."""
    org_id = session.metadata.get("organization_id")
    if not org_id:
        return

    result = await db.execute(
        select(Organization).where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return

    # Cancel any existing subscription before setting up the new one
    # This handles upgrades/downgrades - user only pays for one subscription
    if org.stripe_subscription_id and org.stripe_subscription_id != session.subscription:
        try:
            stripe.Subscription.cancel(org.stripe_subscription_id)
        except stripe.error.InvalidRequestError:
            # Subscription might already be canceled or not exist
            pass

    # Get subscription details
    subscription = stripe.Subscription.retrieve(session.subscription)

    # Determine plan from price (handles both monthly and yearly)
    price_id = subscription["items"]["data"][0]["price"]["id"]
    plan = get_plan_from_price_id(price_id)

    org.stripe_subscription_id = subscription.id
    org.subscription_plan = plan
    org.subscription_status = "active"
    # Handle both old and new Stripe API structures for period_end
    period_end = subscription["items"]["data"][0].get("current_period_end") or subscription.get("current_period_end")
    if period_end:
        org.subscription_period_end = datetime.fromtimestamp(period_end)

    await db.commit()


async def handle_subscription_updated(subscription, db: AsyncSession):
    """Handle subscription updates."""
    customer_id = subscription.customer

    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return

    # Update status
    org.subscription_status = subscription.status
    # Handle both old and new Stripe API structures for period_end
    period_end = subscription["items"]["data"][0].get("current_period_end") or subscription.get("current_period_end")
    if period_end:
        org.subscription_period_end = datetime.fromtimestamp(period_end)

    # Update plan if changed (handles both monthly and yearly)
    price_id = subscription["items"]["data"][0]["price"]["id"]
    plan = get_plan_from_price_id(price_id)
    if plan != "free":
        org.subscription_plan = plan

    await db.commit()


async def handle_subscription_deleted(subscription, db: AsyncSession):
    """Handle subscription cancellation."""
    customer_id = subscription.customer

    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return

    # Only downgrade to free if this is the current subscription
    # This prevents race conditions when upgrading (old sub cancelled, new sub created)
    if org.stripe_subscription_id == subscription.id:
        org.subscription_plan = "free"
        org.subscription_status = "canceled"
        org.stripe_subscription_id = None
        await db.commit()


async def handle_payment_failed(invoice, db: AsyncSession):
    """Handle failed payment."""
    customer_id = invoice.customer

    result = await db.execute(
        select(Organization).where(Organization.stripe_customer_id == customer_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        return

    org.subscription_status = "past_due"

    await db.commit()
