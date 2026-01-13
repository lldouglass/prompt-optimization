"""Video workflow API endpoints."""

import json
import uuid
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..auth import get_current_org_dual, get_user_from_session
from ..models import Organization, VideoWorkflow
from ..schemas.video_workflow import (
    CreateVideoWorkflowRequest,
    VideoWorkflowResponse,
    VideoWorkflowDetailResponse,
    BriefIntakeRequest,
    AnswerQuestionsRequest,
    UpdateContinuityRequest,
    UpdateShotRequest,
    UpdatePromptRequest,
    GeneratePromptsRequest,
    SaveVersionRequest,
    CreateTemplateRequest,
    CreateFromTemplateRequest,
    ExportWorkflowRequest,
    ExportWorkflowResponse,
    ExportFormat,
    BriefData,
    ClarifyingQuestion,
    ContinuityPackData,
    ShotPlanData,
    ShotData,
    PromptPackData,
    ShotPromptData,
    QAScoreData,
    VersionSnapshot,
)
from ..services.video_workflow import (
    generate_clarifying_questions,
    generate_continuity_pack,
    generate_shot_plan,
    generate_prompt_pack,
    score_workflow,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/video-workflows", tags=["video-workflows"])


# ============================================================================
# Helper Functions
# ============================================================================

async def get_workflow_or_404(
    workflow_id: str,
    db: AsyncSession,
    org: Organization,
) -> VideoWorkflow:
    """Get a workflow by ID, checking ownership."""
    try:
        wid = uuid.UUID(workflow_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid workflow ID")

    result = await db.execute(
        select(VideoWorkflow)
        .where(VideoWorkflow.id == wid)
        .where(VideoWorkflow.org_id == org.id)
    )
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow


def workflow_to_response(workflow: VideoWorkflow) -> VideoWorkflowResponse:
    """Convert workflow model to response."""
    shot_count = 0
    if workflow.shot_plan and workflow.shot_plan.get("shots"):
        shot_count = len(workflow.shot_plan["shots"])

    prompt_count = 0
    if workflow.prompt_pack and workflow.prompt_pack.get("prompts"):
        prompt_count = len(workflow.prompt_pack["prompts"])

    overall_score = None
    if workflow.qa_score:
        overall_score = workflow.qa_score.get("overall_score")

    return VideoWorkflowResponse(
        id=str(workflow.id),
        name=workflow.name,
        current_step=workflow.current_step,
        status=workflow.status,
        is_template=workflow.is_template,
        template_name=workflow.template_name,
        shot_count=shot_count,
        prompt_count=prompt_count,
        overall_score=overall_score,
        created_by=str(workflow.created_by) if workflow.created_by else None,
        created_at=workflow.created_at.isoformat(),
        updated_at=workflow.updated_at.isoformat(),
    )


def workflow_to_detail_response(workflow: VideoWorkflow) -> VideoWorkflowDetailResponse:
    """Convert workflow model to detailed response."""
    # Parse JSONB fields into Pydantic models
    brief = None
    if workflow.brief:
        try:
            brief = BriefData(**workflow.brief)
        except Exception:
            brief = workflow.brief

    continuity = None
    if workflow.continuity_pack:
        try:
            continuity = ContinuityPackData(**workflow.continuity_pack)
        except Exception:
            continuity = workflow.continuity_pack

    shot_plan = None
    if workflow.shot_plan:
        try:
            shot_plan = ShotPlanData(**workflow.shot_plan)
        except Exception:
            shot_plan = workflow.shot_plan

    prompt_pack = None
    if workflow.prompt_pack:
        try:
            prompt_pack = PromptPackData(**workflow.prompt_pack)
        except Exception:
            prompt_pack = workflow.prompt_pack

    qa_score = None
    if workflow.qa_score:
        try:
            qa_score = QAScoreData(**workflow.qa_score)
        except Exception:
            qa_score = workflow.qa_score

    versions = []
    if workflow.versions:
        for v in workflow.versions:
            try:
                versions.append(VersionSnapshot(**v))
            except Exception:
                versions.append(v)

    return VideoWorkflowDetailResponse(
        id=str(workflow.id),
        name=workflow.name,
        current_step=workflow.current_step,
        status=workflow.status,
        is_template=workflow.is_template,
        template_name=workflow.template_name,
        source_template_id=str(workflow.source_template_id) if workflow.source_template_id else None,
        brief=brief,
        continuity_pack=continuity,
        shot_plan=shot_plan,
        prompt_pack=prompt_pack,
        qa_score=qa_score,
        versions=versions,
        created_by=str(workflow.created_by) if workflow.created_by else None,
        created_at=workflow.created_at.isoformat(),
        updated_at=workflow.updated_at.isoformat(),
    )


# ============================================================================
# Workflow CRUD
# ============================================================================

@router.post("", response_model=VideoWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    data: CreateVideoWorkflowRequest,
    request=None,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Create a new video workflow."""
    from fastapi import Request
    if request is None:
        user_id = None
    else:
        user = await get_user_from_session(request, db)
        user_id = user.id if user else None

    workflow = VideoWorkflow(
        org_id=org.id,
        name=data.name,
        created_by=user_id,
        current_step=1,
        status="draft",
        versions=[],
    )

    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    logger.info(f"Created video workflow {workflow.id} for org {org.id}")
    return workflow_to_response(workflow)


@router.get("", response_model=list[VideoWorkflowResponse])
async def list_workflows(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    include_templates: bool = Query(False),
):
    """List all video workflows for the organization."""
    query = select(VideoWorkflow).where(VideoWorkflow.org_id == org.id)

    if not include_templates:
        query = query.where(VideoWorkflow.is_template == False)

    query = query.order_by(desc(VideoWorkflow.updated_at)).limit(limit).offset(offset)

    result = await db.execute(query)
    workflows = result.scalars().all()

    return [workflow_to_response(w) for w in workflows]


@router.get("/templates", response_model=list[VideoWorkflowResponse])
async def list_templates(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """List all workflow templates."""
    result = await db.execute(
        select(VideoWorkflow)
        .where(VideoWorkflow.org_id == org.id)
        .where(VideoWorkflow.is_template == True)
        .order_by(desc(VideoWorkflow.created_at))
    )
    templates = result.scalars().all()
    return [workflow_to_response(t) for t in templates]


@router.get("/{workflow_id}", response_model=VideoWorkflowDetailResponse)
async def get_workflow(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Get a video workflow by ID with full details."""
    workflow = await get_workflow_or_404(workflow_id, db, org)
    return workflow_to_detail_response(workflow)


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Delete a video workflow."""
    workflow = await get_workflow_or_404(workflow_id, db, org)
    await db.delete(workflow)
    await db.commit()
    logger.info(f"Deleted video workflow {workflow_id}")


# ============================================================================
# Step 1-2: Brief & Questions
# ============================================================================

@router.put("/{workflow_id}/brief")
async def save_brief(
    workflow_id: str,
    data: BriefIntakeRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Save or update the brief intake data."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    # Merge with existing brief to preserve clarifying_questions
    existing_brief = workflow.brief or {}
    clarifying_questions = existing_brief.get("clarifying_questions", [])

    workflow.brief = {
        **data.model_dump(),
        "clarifying_questions": clarifying_questions,
    }
    workflow.current_step = max(workflow.current_step, 1)
    workflow.status = "in_progress"
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"message": "Brief saved", "brief": workflow.brief}


@router.post("/{workflow_id}/questions")
async def generate_questions_endpoint(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Generate clarifying questions based on the brief."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.brief:
        raise HTTPException(status_code=400, detail="Brief must be saved first")

    try:
        questions = await generate_clarifying_questions(workflow.brief)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save questions to brief
    workflow.brief["clarifying_questions"] = questions
    workflow.current_step = max(workflow.current_step, 2)
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"questions": questions}


@router.post("/{workflow_id}/questions/answer")
async def submit_answers(
    workflow_id: str,
    data: AnswerQuestionsRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Submit answers to clarifying questions."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.brief or not workflow.brief.get("clarifying_questions"):
        raise HTTPException(status_code=400, detail="No questions to answer")

    # Update answers in questions
    for question in workflow.brief["clarifying_questions"]:
        if question["id"] in data.answers:
            question["answer"] = data.answers[question["id"]]

    workflow.current_step = max(workflow.current_step, 2)
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"message": "Answers saved", "questions": workflow.brief["clarifying_questions"]}


# ============================================================================
# Step 3: Continuity Pack
# ============================================================================

@router.post("/{workflow_id}/continuity")
async def generate_continuity_endpoint(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Generate continuity pack from brief and Q&A."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.brief:
        raise HTTPException(status_code=400, detail="Brief must be completed first")

    # Build answers dict from questions
    answers = {}
    for q in workflow.brief.get("clarifying_questions", []):
        if q.get("answer"):
            answers[q["id"]] = q["answer"]

    try:
        continuity = await generate_continuity_pack(workflow.brief, answers)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    workflow.continuity_pack = continuity
    workflow.current_step = max(workflow.current_step, 3)
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"continuity_pack": continuity}


@router.put("/{workflow_id}/continuity")
async def update_continuity(
    workflow_id: str,
    data: UpdateContinuityRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Manually update continuity pack."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.continuity_pack:
        workflow.continuity_pack = {}

    # Merge updates
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        if isinstance(value, list):
            workflow.continuity_pack[key] = [
                v.model_dump() if hasattr(v, "model_dump") else v for v in value
            ]
        elif hasattr(value, "model_dump"):
            workflow.continuity_pack[key] = value.model_dump()
        else:
            workflow.continuity_pack[key] = value

    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"continuity_pack": workflow.continuity_pack}


# ============================================================================
# Step 4: Shot Plan
# ============================================================================

@router.post("/{workflow_id}/shots")
async def generate_shots_endpoint(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Generate shot plan from brief and continuity."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.brief:
        raise HTTPException(status_code=400, detail="Brief must be completed first")
    if not workflow.continuity_pack:
        raise HTTPException(status_code=400, detail="Continuity pack must be completed first")

    try:
        shot_plan = await generate_shot_plan(workflow.brief, workflow.continuity_pack)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    workflow.shot_plan = shot_plan
    workflow.current_step = max(workflow.current_step, 4)
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"shot_plan": shot_plan}


@router.put("/{workflow_id}/shots/{shot_index}")
async def update_shot(
    workflow_id: str,
    shot_index: int,
    data: UpdateShotRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Update a single shot in the shot plan."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.shot_plan or not workflow.shot_plan.get("shots"):
        raise HTTPException(status_code=400, detail="No shot plan exists")

    shots = workflow.shot_plan["shots"]
    if shot_index < 0 or shot_index >= len(shots):
        raise HTTPException(status_code=400, detail="Shot index out of range")

    # Update shot with provided fields
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        shots[shot_index][key] = value

    workflow.shot_plan["shots"] = shots
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"shot": shots[shot_index]}


# ============================================================================
# Step 5: Prompt Pack
# ============================================================================

@router.post("/{workflow_id}/prompts")
async def generate_prompts_endpoint(
    workflow_id: str,
    data: GeneratePromptsRequest = None,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Generate prompt pack for all shots."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.shot_plan or not workflow.shot_plan.get("shots"):
        raise HTTPException(status_code=400, detail="Shot plan must be completed first")
    if not workflow.continuity_pack:
        raise HTTPException(status_code=400, detail="Continuity pack must be completed first")

    target_model = "sora_2"
    if data:
        target_model = data.target_model

    try:
        prompt_pack = await generate_prompt_pack(
            workflow.shot_plan["shots"],
            workflow.continuity_pack,
            workflow.brief or {},
            target_model,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    workflow.prompt_pack = prompt_pack
    workflow.current_step = max(workflow.current_step, 5)
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"prompt_pack": prompt_pack}


@router.put("/{workflow_id}/prompts/{prompt_index}")
async def update_prompt(
    workflow_id: str,
    prompt_index: int,
    data: UpdatePromptRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Update a single prompt in the prompt pack."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if not workflow.prompt_pack or not workflow.prompt_pack.get("prompts"):
        raise HTTPException(status_code=400, detail="No prompt pack exists")

    prompts = workflow.prompt_pack["prompts"]
    if prompt_index < 0 or prompt_index >= len(prompts):
        raise HTTPException(status_code=400, detail="Prompt index out of range")

    # Update prompt with provided fields
    updates = data.model_dump(exclude_none=True)
    for key, value in updates.items():
        if hasattr(value, "model_dump"):
            prompts[prompt_index][key] = value.model_dump()
        else:
            prompts[prompt_index][key] = value

    workflow.prompt_pack["prompts"] = prompts
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"prompt": prompts[prompt_index]}


# ============================================================================
# Step 6: QA Score
# ============================================================================

@router.post("/{workflow_id}/qa")
async def run_qa_scoring(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Run QA scoring on the workflow."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    shots = []
    if workflow.shot_plan and workflow.shot_plan.get("shots"):
        shots = workflow.shot_plan["shots"]

    prompts = []
    if workflow.prompt_pack and workflow.prompt_pack.get("prompts"):
        prompts = workflow.prompt_pack["prompts"]

    if not shots or not prompts:
        raise HTTPException(
            status_code=400,
            detail="Shot plan and prompt pack must be completed first"
        )

    qa_result = score_workflow(
        brief=workflow.brief,
        continuity=workflow.continuity_pack,
        shots=shots,
        prompts=prompts,
    )

    workflow.qa_score = qa_result
    workflow.current_step = max(workflow.current_step, 6)
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"qa_score": qa_result}


# ============================================================================
# Step 7: Versions, Export, Templates
# ============================================================================

@router.post("/{workflow_id}/versions")
async def save_version(
    workflow_id: str,
    data: SaveVersionRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Save current state as a version snapshot."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    # Get the data for the specified step
    step_data = None
    if data.step == "brief":
        step_data = workflow.brief
    elif data.step == "continuity":
        step_data = workflow.continuity_pack
    elif data.step == "shots":
        step_data = workflow.shot_plan
    elif data.step == "prompts":
        step_data = workflow.prompt_pack
    else:
        raise HTTPException(status_code=400, detail="Invalid step name")

    if not step_data:
        raise HTTPException(status_code=400, detail=f"No data for step: {data.step}")

    # Calculate next version number for this step
    versions = workflow.versions or []
    step_versions = [v for v in versions if v.get("step") == data.step]
    next_version = len(step_versions) + 1

    # Create version snapshot
    version = {
        "version_number": next_version,
        "step": data.step,
        "data": step_data,
        "created_at": datetime.utcnow().isoformat(),
    }

    versions.append(version)
    workflow.versions = versions
    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"version": version, "total_versions": len(versions)}


@router.get("/{workflow_id}/versions")
async def list_versions(
    workflow_id: str,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """List all version snapshots for a workflow."""
    workflow = await get_workflow_or_404(workflow_id, db, org)
    return {"versions": workflow.versions or []}


@router.post("/{workflow_id}/restore/{version_index}")
async def restore_version(
    workflow_id: str,
    version_index: int,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Restore a workflow to a previous version."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    versions = workflow.versions or []
    if version_index < 0 or version_index >= len(versions):
        raise HTTPException(status_code=400, detail="Version index out of range")

    version = versions[version_index]
    step = version.get("step")
    data = version.get("data")

    if step == "brief":
        workflow.brief = data
    elif step == "continuity":
        workflow.continuity_pack = data
    elif step == "shots":
        workflow.shot_plan = data
    elif step == "prompts":
        workflow.prompt_pack = data

    workflow.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(workflow)

    return {"message": f"Restored {step} to version {version.get('version_number')}"}


@router.get("/{workflow_id}/export")
async def export_workflow(
    workflow_id: str,
    format: ExportFormat = Query(ExportFormat.JSON),
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Export workflow as JSON or Markdown."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    if format == ExportFormat.JSON:
        content = json.dumps({
            "name": workflow.name,
            "brief": workflow.brief,
            "continuity_pack": workflow.continuity_pack,
            "shot_plan": workflow.shot_plan,
            "prompt_pack": workflow.prompt_pack,
            "qa_score": workflow.qa_score,
        }, indent=2)
        filename = f"{workflow.name.replace(' ', '_')}_workflow.json"

    else:  # Markdown
        content = _generate_markdown_export(workflow)
        filename = f"{workflow.name.replace(' ', '_')}_workflow.md"

    return ExportWorkflowResponse(
        format=format,
        filename=filename,
        content=content,
    )


def _generate_markdown_export(workflow: VideoWorkflow) -> str:
    """Generate Markdown export of workflow."""
    lines = [f"# {workflow.name}", ""]

    # Brief
    if workflow.brief:
        lines.extend([
            "## Brief",
            f"**Goal:** {workflow.brief.get('goal', 'N/A')}",
            f"**Platform:** {workflow.brief.get('platform', 'N/A')}",
            f"**Duration:** {workflow.brief.get('duration_seconds', 'N/A')} seconds",
            f"**Aspect Ratio:** {workflow.brief.get('aspect_ratio', 'N/A')}",
            "",
            f"**Subject:** {workflow.brief.get('product_or_subject_description', 'N/A')}",
            "",
        ])

    # Continuity Pack
    if workflow.continuity_pack:
        lines.extend(["## Continuity Pack", ""])

        if workflow.continuity_pack.get("style_clause"):
            lines.extend([
                "### Style",
                workflow.continuity_pack["style_clause"],
                "",
            ])

        if workflow.continuity_pack.get("anchors"):
            lines.append("### Visual Anchors")
            for anchor in workflow.continuity_pack["anchors"]:
                lines.append(f"- **{anchor.get('type', 'Unknown')}:** {anchor.get('description', '')}")
            lines.append("")

    # Shot Plan
    if workflow.shot_plan and workflow.shot_plan.get("shots"):
        lines.extend(["## Shot Plan", ""])
        for shot in workflow.shot_plan["shots"]:
            lines.extend([
                f"### Shot {shot.get('shot_number', '?')}: {shot.get('start_sec', 0):.1f}s - {shot.get('end_sec', 0):.1f}s",
                f"**Type:** {shot.get('shot_type', 'N/A')} | **Camera:** {shot.get('camera_move', 'none')}",
                "",
                shot.get("framing_notes", ""),
                "",
                "**Actions:**",
            ])
            for beat in shot.get("subject_action_beats", []):
                lines.append(f"- {beat}")
            lines.extend(["", f"**Purpose:** {shot.get('purpose', 'N/A')}", ""])

    # Prompt Pack
    if workflow.prompt_pack and workflow.prompt_pack.get("prompts"):
        lines.extend([
            "## Sora 2 Prompts",
            f"**Target Model:** {workflow.prompt_pack.get('target_model', 'sora_2')}",
            "",
        ])
        for i, prompt in enumerate(workflow.prompt_pack["prompts"], 1):
            lines.extend([
                f"### Prompt {i}",
                "```",
                prompt.get("prompt_text", ""),
                "```",
                "",
            ])
            if prompt.get("negative_prompt_text"):
                lines.extend([
                    "**Negative:**",
                    prompt["negative_prompt_text"],
                    "",
                ])

    # QA Score
    if workflow.qa_score:
        lines.extend([
            "## QA Score",
            f"**Overall Score:** {workflow.qa_score.get('overall_score', 'N/A')}/100",
            "",
            f"- Ambiguity Risk: {workflow.qa_score.get('ambiguity_risk', 'N/A')}",
            f"- Motion Complexity: {workflow.qa_score.get('motion_complexity_risk', 'N/A')}",
            f"- Continuity Completeness: {workflow.qa_score.get('continuity_completeness', 'N/A')}",
            f"- Audio Readiness: {workflow.qa_score.get('audio_readiness', 'N/A')}",
            "",
        ])

        if workflow.qa_score.get("warnings"):
            lines.append("### Warnings")
            for warning in workflow.qa_score["warnings"]:
                lines.append(f"- {warning}")
            lines.append("")

    return "\n".join(lines)


@router.post("/{workflow_id}/template")
async def create_template(
    workflow_id: str,
    data: CreateTemplateRequest,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Create a template from a workflow."""
    workflow = await get_workflow_or_404(workflow_id, db, org)

    # Create a copy as template
    template = VideoWorkflow(
        org_id=org.id,
        name=f"Template: {data.template_name}",
        is_template=True,
        template_name=data.template_name,
        source_template_id=workflow.id,
        brief=workflow.brief,
        continuity_pack=workflow.continuity_pack,
        shot_plan=workflow.shot_plan,
        # Don't copy prompts or QA score - those are specific to content
        current_step=4 if workflow.shot_plan else (3 if workflow.continuity_pack else 1),
        status="completed",
        versions=[],
    )

    db.add(template)
    await db.commit()
    await db.refresh(template)

    logger.info(f"Created template {template.id} from workflow {workflow_id}")
    return workflow_to_response(template)


@router.post("/from-template/{template_id}")
async def create_from_template(
    template_id: str,
    data: CreateFromTemplateRequest,
    request=None,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workflow from a template."""
    from fastapi import Request

    template = await get_workflow_or_404(template_id, db, org)

    if not template.is_template:
        raise HTTPException(status_code=400, detail="Workflow is not a template")

    if request is None:
        user_id = None
    else:
        user = await get_user_from_session(request, db)
        user_id = user.id if user else None

    # Create new workflow from template
    workflow = VideoWorkflow(
        org_id=org.id,
        name=data.name,
        created_by=user_id,
        source_template_id=template.id,
        brief=template.brief,
        continuity_pack=template.continuity_pack,
        shot_plan=template.shot_plan,
        current_step=template.current_step,
        status="in_progress",
        versions=[],
    )

    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    logger.info(f"Created workflow {workflow.id} from template {template_id}")
    return workflow_to_response(workflow)
