from uuid import UUID
from datetime import datetime
from typing import Any
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Organization, Request
from ..auth import get_current_org

router = APIRouter(prefix="/api/v1/requests", tags=["requests"])


class RequestResponse(BaseModel):
    id: UUID
    model: str
    provider: str
    messages: list[dict[str, Any]]
    parameters: dict[str, Any] | None
    response_content: str | None
    latency_ms: int | None
    input_tokens: int | None
    output_tokens: int | None
    cost_usd: Decimal | None
    prompt_id: UUID | None
    tags: dict[str, Any] | None
    trace_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[RequestResponse])
async def list_requests(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    trace_id: str | None = Query(None),
) -> list[Request]:
    """List logged requests for the authenticated organization."""
    query = select(Request).where(Request.org_id == org.id)

    if trace_id:
        query = query.where(Request.trace_id == trace_id)

    query = query.order_by(Request.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{request_id}", response_model=RequestResponse)
async def get_request(
    request_id: UUID,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> Request:
    """Get a specific request by ID."""
    result = await db.execute(
        select(Request).where(Request.id == request_id, Request.org_id == org.id)
    )
    request = result.scalar_one_or_none()
    if not request:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request
