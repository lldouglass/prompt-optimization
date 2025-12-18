import hashlib
from datetime import datetime
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from .models import ApiKey, Organization

security = HTTPBearer()


def hash_api_key(key: str) -> str:
    """Hash an API key using SHA256."""
    return hashlib.sha256(key.encode()).hexdigest()


async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    """Validate API key and return the API key record."""
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
