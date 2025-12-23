"""Router for authentication endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..config import get_settings
from ..models import User, Organization, OrganizationMember, UserSession
from ..auth_utils import hash_password, verify_password, generate_session_token, hash_session_token, generate_verification_token
from ..email import send_verification_email
from ..schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
    OrganizationBasicResponse,
    MembershipResponse,
    MessageResponse,
    VerifyEmailRequest,
    ResendVerificationRequest,
)

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
settings = get_settings()


def get_session_cookie_name() -> str:
    return settings.session_cookie_name


async def create_session(
    user: User,
    db: AsyncSession,
    response: Response,
    request: Request,
) -> None:
    """Create a new session and set the cookie."""
    token = generate_session_token()
    token_hash = hash_session_token(token)
    expires_at = datetime.utcnow() + timedelta(days=settings.session_expire_days)

    session = UserSession(
        user_id=user.id,
        session_token_hash=token_hash,
        expires_at=expires_at,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    db.add(session)
    await db.commit()

    # Set HTTP-only cookie
    # For cross-domain (frontend/backend on different domains), need secure=True and samesite="none"
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=settings.session_expire_days * 24 * 60 * 60,
        path="/",
    )


async def get_user_auth_response(user: User, db: AsyncSession) -> AuthResponse:
    """Build the auth response with user and memberships."""
    # Fetch memberships with organizations
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id)
        .options(selectinload(OrganizationMember.organization))
    )
    memberships = result.scalars().all()

    membership_responses = []
    current_org = None

    for m in memberships:
        org_response = OrganizationBasicResponse(
            id=m.organization.id,
            name=m.organization.name,
            subscription_plan=m.organization.subscription_plan,
        )
        membership_responses.append(
            MembershipResponse(organization=org_response, role=m.role)
        )
        # First org becomes current (or the one where user is owner)
        if current_org is None or m.role == "owner":
            current_org = org_response

    return AuthResponse(
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            avatar_url=user.avatar_url,
            email_verified=user.email_verified,
            created_at=user.created_at,
        ),
        memberships=membership_responses,
        current_organization=current_org,
    )


@router.post("/register", response_model=AuthResponse)
async def register(
    request_data: RegisterRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Register a new user with email and password."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate verification token
    verification_token = generate_verification_token()
    verification_expires = datetime.utcnow() + timedelta(hours=settings.verification_token_expire_hours)

    # Create user
    user = User(
        email=request_data.email,
        password_hash=hash_password(request_data.password),
        name=request_data.name,
        email_verified=False,
        verification_token=verification_token,
        verification_token_expires=verification_expires,
    )
    db.add(user)
    await db.flush()  # Get user.id

    # Create organization
    org = Organization(name=request_data.organization_name)
    db.add(org)
    await db.flush()  # Get org.id

    # Create membership (user is owner)
    membership = OrganizationMember(
        org_id=org.id,
        user_id=user.id,
        role="owner",
        joined_at=datetime.utcnow(),
    )
    db.add(membership)
    await db.commit()

    # Send verification email (don't block on failure)
    await send_verification_email(request_data.email, verification_token, request_data.name)

    # Update user's last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create session
    await create_session(user, db, response, request)

    return await get_user_auth_response(user, db)


@router.post("/login", response_model=AuthResponse)
async def login(
    request_data: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Log in with email and password."""
    # Find user
    result = await db.execute(select(User).where(User.email == request_data.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(request_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Create session
    await create_session(user, db, response, request)

    return await get_user_auth_response(user, db)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Log out and invalidate the session."""
    token = request.cookies.get(settings.session_cookie_name)

    if token:
        token_hash = hash_session_token(token)
        result = await db.execute(
            select(UserSession).where(UserSession.session_token_hash == token_hash)
        )
        session = result.scalar_one_or_none()
        if session:
            await db.delete(session)
            await db.commit()

    # Clear cookie
    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
    )

    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=AuthResponse)
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """Get the current authenticated user."""
    token = request.cookies.get(settings.session_cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token_hash = hash_session_token(token)
    result = await db.execute(
        select(UserSession)
        .where(UserSession.session_token_hash == token_hash)
        .options(selectinload(UserSession.user))
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )

    if session.expires_at < datetime.utcnow():
        await db.delete(session)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    # Update last activity
    session.last_activity_at = datetime.utcnow()
    await db.commit()

    return await get_user_auth_response(session.user, db)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request_data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Verify a user's email address with the verification token."""
    # Find user by verification token
    result = await db.execute(
        select(User).where(User.verification_token == request_data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    # Check if token is expired
    if user.verification_token_expires and user.verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one.",
        )

    # Mark email as verified
    user.email_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    await db.commit()

    return MessageResponse(message="Email verified successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    request_data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Resend the verification email to a user."""
    # Find user by email
    result = await db.execute(select(User).where(User.email == request_data.email))
    user = result.scalar_one_or_none()

    # Always return success to prevent email enumeration
    if not user:
        return MessageResponse(message="If an account exists with this email, a verification email has been sent.")

    # Check if already verified
    if user.email_verified:
        return MessageResponse(message="Email is already verified.")

    # Generate new verification token
    verification_token = generate_verification_token()
    verification_expires = datetime.utcnow() + timedelta(hours=settings.verification_token_expire_hours)

    user.verification_token = verification_token
    user.verification_token_expires = verification_expires
    await db.commit()

    # Send verification email
    await send_verification_email(request_data.email, verification_token, user.name)

    return MessageResponse(message="If an account exists with this email, a verification email has been sent.")
