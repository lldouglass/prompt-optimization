import secrets
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Organization, ApiKey
from ..schemas.admin import (
    OrganizationCreate,
    OrganizationResponse,
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyCreateResponse,
)
from ..auth import hash_api_key
from ..config import get_settings

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
settings = get_settings()


# Organization endpoints
@router.post("/organizations", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """Create a new organization."""
    org = Organization(name=data.name)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


@router.get("/organizations", response_model=list[OrganizationResponse])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
) -> list[Organization]:
    """List all organizations."""
    result = await db.execute(select(Organization).order_by(Organization.created_at.desc()))
    return list(result.scalars().all())


@router.get("/organizations/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Organization:
    """Get an organization by ID."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return org


# API Key endpoints
@router.post("/organizations/{org_id}/api-keys", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    org_id: UUID,
    data: ApiKeyCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Create a new API key for an organization. The raw key is only returned once!"""
    # Verify org exists
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    # Generate the API key
    raw_key = f"{settings.api_key_prefix}{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(raw_key)
    key_prefix = raw_key[:16]

    api_key = ApiKey(
        org_id=org_id,
        key_hash=key_hash,
        key_prefix=key_prefix,
        name=data.name,
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    # Return the raw key along with the record (only time it's visible)
    return {
        "id": api_key.id,
        "key": raw_key,
        "key_prefix": api_key.key_prefix,
        "name": api_key.name,
        "created_at": api_key.created_at,
        "last_used_at": api_key.last_used_at,
    }


@router.get("/organizations/{org_id}/api-keys", response_model=list[ApiKeyResponse])
async def list_api_keys(
    org_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[ApiKey]:
    """List all API keys for an organization (without the actual keys)."""
    # Verify org exists
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

    result = await db.execute(
        select(ApiKey).where(ApiKey.org_id == org_id).order_by(ApiKey.created_at.desc())
    )
    return list(result.scalars().all())


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an API key."""
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    await db.delete(api_key)
    await db.commit()
