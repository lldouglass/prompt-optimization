import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from ..database import get_db
from ..auth import get_api_key
from ..models.api_key import ApiKey
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

router = APIRouter(prefix="/billing", tags=["billing"])
settings = get_settings()


def init_stripe():
    if settings.stripe_secret_key:
        stripe.api_key = settings.stripe_secret_key


@router.get("", response_model=BillingInfo)
async def get_billing_info(
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Get current billing and usage information."""
    result = await db.execute(
        select(Organization).where(Organization.id == api_key.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    limits = get_plan_limits(org.subscription_plan)

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
            optimizations_limit=limits["optimizations_per_month"],
            usage_reset_at=org.usage_reset_at,
        ),
    )


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutRequest,
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe checkout session for subscription."""
    init_stripe()

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    result = await db.execute(
        select(Organization).where(Organization.id == api_key.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # Get price ID based on plan
    price_id = None
    if request.plan == "pro":
        price_id = settings.stripe_price_pro
    elif request.plan == "team":
        price_id = settings.stripe_price_team
    else:
        raise HTTPException(status_code=400, detail="Invalid plan")

    if not price_id:
        raise HTTPException(status_code=503, detail=f"Price for {request.plan} not configured")

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
    api_key: ApiKey = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
):
    """Create a Stripe customer portal session for managing subscription."""
    init_stripe()

    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    result = await db.execute(
        select(Organization).where(Organization.id == api_key.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

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

    # Get subscription details
    subscription = stripe.Subscription.retrieve(session.subscription)

    # Determine plan from price
    price_id = subscription["items"]["data"][0]["price"]["id"]
    if price_id == settings.stripe_price_pro:
        plan = "pro"
    elif price_id == settings.stripe_price_team:
        plan = "team"
    else:
        plan = "free"

    org.stripe_subscription_id = subscription.id
    org.subscription_plan = plan
    org.subscription_status = "active"
    org.subscription_period_end = datetime.fromtimestamp(subscription.current_period_end)

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
    org.subscription_period_end = datetime.fromtimestamp(subscription.current_period_end)

    # Update plan if changed
    price_id = subscription["items"]["data"][0]["price"]["id"]
    if price_id == settings.stripe_price_pro:
        org.subscription_plan = "pro"
    elif price_id == settings.stripe_price_team:
        org.subscription_plan = "team"

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
