import sys
from pathlib import Path
from uuid import UUID
from datetime import datetime
from typing import Any
from decimal import Decimal
from fastapi import APIRouter, Depends, Query, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Organization, Request
from ..auth import get_current_org

# Add project root to path for agent imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents import Judge, JudgeError

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
    # Evaluation fields
    evaluation_score: float | None = None
    evaluation_subscores: dict[str, int] | None = None
    evaluation_tags: list[str] | None = None
    evaluation_rationale: str | None = None
    evaluated_at: datetime | None = None

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return request


@router.post("/{request_id}/evaluate", response_model=RequestResponse)
async def evaluate_request(
    request_id: UUID,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> Request:
    """Manually trigger evaluation for a specific request."""
    result = await db.execute(
        select(Request).where(Request.id == request_id, Request.org_id == org.id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if not request.response_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot evaluate request without response content"
        )

    # Extract user input from messages
    user_input = ""
    task_description = "Respond to user query"
    for msg in request.messages:
        if msg.get("role") == "user":
            user_input = msg.get("content", "")
        elif msg.get("role") == "system":
            task_description = msg.get("content", task_description)

    if not user_input:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot evaluate request without user message"
        )

    try:
        # Run Judge evaluation
        judge = Judge(model="gpt-4o-mini")
        eval_result = judge.evaluate_single(
            task_description=task_description,
            user_input=user_input,
            candidate_output=request.response_content
        )

        # Update the request with evaluation results
        request.evaluation_score = eval_result.get("overall_score")
        request.evaluation_subscores = eval_result.get("subscores")
        request.evaluation_tags = eval_result.get("tags", [])
        request.evaluation_rationale = eval_result.get("rationale", "")
        request.evaluated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(request)
        return request
    except JudgeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )
