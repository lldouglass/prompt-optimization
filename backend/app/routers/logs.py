import sys
from datetime import datetime
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models import Organization, Prompt, Request
from ..schemas import LogCreate, LogResponse
from ..auth import get_current_org

# Add project root to path for agent imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from agents import Judge, JudgeError

router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


async def evaluate_request_background(request_id: UUID, db_url: str):
    """Background task to evaluate a logged request using the Judge agent."""
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import select

    engine = create_async_engine(db_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Get the request
        result = await session.execute(select(Request).where(Request.id == request_id))
        request = result.scalar_one_or_none()

        if not request or not request.response_content:
            return

        # Extract user input from messages
        user_input = ""
        task_description = "Respond to user query"
        for msg in request.messages:
            if msg.get("role") == "user":
                user_input = msg.get("content", "")
            elif msg.get("role") == "system":
                task_description = msg.get("content", task_description)

        if not user_input:
            return

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

            await session.commit()
        except JudgeError:
            pass  # Silently fail on evaluation errors
        except Exception:
            pass  # Don't crash on unexpected errors

    await engine.dispose()


@router.post("", response_model=LogResponse, status_code=status.HTTP_201_CREATED)
async def create_log(
    log_data: LogCreate,
    background_tasks: BackgroundTasks,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
) -> Request:
    """Log a new LLM request and trigger automatic evaluation."""
    from ..config import get_settings
    settings = get_settings()

    # Look up prompt by slug if provided
    prompt_id: UUID | None = None
    if log_data.prompt_slug:
        result = await db.execute(
            select(Prompt).where(
                Prompt.org_id == org.id,
                Prompt.slug == log_data.prompt_slug,
            )
        )
        prompt = result.scalar_one_or_none()
        if prompt:
            prompt_id = prompt.id

    # Create the request record
    request = Request(
        org_id=org.id,
        model=log_data.model,
        provider=log_data.provider,
        messages=log_data.messages,
        parameters=log_data.parameters,
        response_content=log_data.response_content,
        response_raw=log_data.response_raw,
        latency_ms=log_data.latency_ms,
        input_tokens=log_data.input_tokens,
        output_tokens=log_data.output_tokens,
        cost_usd=log_data.cost_usd,
        prompt_id=prompt_id,
        tags=log_data.tags,
        trace_id=log_data.trace_id,
    )

    db.add(request)
    await db.commit()
    await db.refresh(request)

    # Trigger background evaluation if response content exists
    if log_data.response_content:
        background_tasks.add_task(
            evaluate_request_background,
            request.id,
            settings.database_url
        )

    return request
