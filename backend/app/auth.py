import hashlib
from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .database import get_db
from .models import ApiKey, Organization, User, UserSession, OrganizationMember
from .auth_utils import hash_session_token
from .config import get_settings

security = HTTPBearer(auto_error=False)  # Don't auto-error, we'll handle missing auth
settings = get_settings()


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA256."""
    return hashlib.sha256(key.encode()).hexdigest()


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    """Validate API key and return the API key record."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    api_key = credentials.credentials
    key_hash = hash_api_key(api_key)

    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash)
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Update last_used_at
    api_key_record.last_used_at = datetime.utcnow()
    await db.commit()

    return api_key_record


async def get_current_org(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """Validate API key and return the associated organization."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    api_key = credentials.credentials
    key_hash = hash_api_key(api_key)

    result = await db.execute(
        select(ApiKey).where(ApiKey.key_hash == key_hash)
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    # Update last_used_at
    api_key_record.last_used_at = datetime.utcnow()
    await db.commit()

    # Fetch the organization
    result = await db.execute(
        select(Organization).where(Organization.id == api_key_record.org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Organization not found",
        )

    return org


async def get_user_from_session(
    request: Request,
    db: AsyncSession,
) -> Optional[User]:
    """Get user from session cookie if valid."""
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        return None

    token_hash = hash_session_token(token)
    result = await db.execute(
        select(UserSession)
        .where(UserSession.session_token_hash == token_hash)
        .options(selectinload(UserSession.user))
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    if session.expires_at < datetime.utcnow():
        await db.delete(session)
        await db.commit()
        return None

    # Update last activity
    session.last_activity_at = datetime.utcnow()
    await db.commit()

    return session.user


async def get_org_from_session(
    user: User,
    db: AsyncSession,
) -> Optional[Organization]:
    """Get user's primary organization from their memberships."""
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id)
        .options(selectinload(OrganizationMember.organization))
        .order_by(OrganizationMember.role.desc())  # owner > admin > member
    )
    membership = result.scalars().first()

    if not membership:
        return None

    return membership.organization


async def get_current_org_dual(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """
    Get current organization via session cookie OR API key.
    Session cookie is checked first (for web app), then API key (for SDK).
    """
    # Try session cookie first
    user = await get_user_from_session(request, db)
    if user:
        org = await get_org_from_session(user, db)
        if org:
            return org
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User has no organization",
        )

    # Fall back to API key
    if credentials:
        api_key = credentials.credentials
        key_hash = hash_api_key(api_key)

        result = await db.execute(
            select(ApiKey).where(ApiKey.key_hash == key_hash)
        )
        api_key_record = result.scalar_one_or_none()

        if api_key_record:
            api_key_record.last_used_at = datetime.utcnow()
            await db.commit()

            result = await db.execute(
                select(Organization).where(Organization.id == api_key_record.org_id)
            )
            org = result.scalar_one_or_none()
            if org:
                return org

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
    )
