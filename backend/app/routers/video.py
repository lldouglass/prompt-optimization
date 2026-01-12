"""Router for video prompt optimization endpoints."""

import hashlib
import logging
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Request
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..config import get_settings
from ..auth import get_user_from_session, get_org_from_session, get_current_org, get_current_org_dual
from ..models import User, Organization
from ..models.video import (
    VideoProject,
    VideoPrompt,
    VideoPromptVersion,
    VideoPromptOutput,
    VideoPromptShareToken,
    generate_full_prompt_text,
)
from ..schemas.video import (
    CreateVideoProjectRequest,
    UpdateVideoProjectRequest,
    VideoProjectResponse,
    VideoProjectListResponse,
    CreateVideoPromptRequest,
    UpdateVideoPromptRequest,
    VideoPromptResponse,
    VideoPromptListResponse,
    CreateVideoPromptVersionRequest,
    RollbackVersionRequest,
    PromoteVariantRequest,
    GenerateVariantsRequest,
    VideoPromptVersionResponse,
    VideoPromptVersionListResponse,
    AttachOutputRequest,
    ScoreOutputRequest,
    VideoPromptOutputResponse,
    VideoPromptOutputListResponse,
    CreateShareTokenRequest,
    ShareTokenResponse,
    ShareTokenListResponse,
    VideoPromptDetailResponse,
    SharedVideoPromptResponse,
    FeatureFlagsResponse,
)

settings = get_settings()
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/video", tags=["video"])


# ============================================================================
# Helper Functions
# ============================================================================


async def get_auth_context(
    request: Request,
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> tuple[Optional[uuid.UUID], Organization]:
    """
    Get (user_id, org) tuple for video endpoints.
    Uses get_current_org_dual for proper session/API key auth.
    user_id may be None for API key auth.
    """
    user = await get_user_from_session(request, db)
    return (user.id if user else None, org)


async def get_project_or_404(
    project_id: str,
    db: AsyncSession,
    org: Organization,
) -> VideoProject:
    """Get a project by ID, checking ownership."""
    try:
        pid = uuid.UUID(project_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    result = await db.execute(
        select(VideoProject)
        .where(VideoProject.id == pid)
        .where(VideoProject.org_id == org.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


async def get_prompt_or_404(
    prompt_id: str,
    db: AsyncSession,
    org: Organization,
) -> VideoPrompt:
    """Get a prompt by ID, checking ownership via project."""
    try:
        pid = uuid.UUID(prompt_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid prompt ID")

    result = await db.execute(
        select(VideoPrompt)
        .join(VideoProject)
        .where(VideoPrompt.id == pid)
        .where(VideoProject.org_id == org.id)
        .options(selectinload(VideoPrompt.versions))
    )
    prompt = result.scalar_one_or_none()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    return prompt


async def get_version_or_404(
    version_id: str,
    db: AsyncSession,
    org: Organization,
) -> VideoPromptVersion:
    """Get a version by ID, checking ownership."""
    try:
        vid = uuid.UUID(version_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid version ID")

    result = await db.execute(
        select(VideoPromptVersion)
        .join(VideoPrompt)
        .join(VideoProject)
        .where(VideoPromptVersion.id == vid)
        .where(VideoProject.org_id == org.id)
        .options(selectinload(VideoPromptVersion.outputs))
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    return version


async def get_output_or_404(
    output_id: str,
    db: AsyncSession,
    org: Organization,
) -> VideoPromptOutput:
    """Get an output by ID, checking ownership."""
    try:
        oid = uuid.UUID(output_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid output ID")

    result = await db.execute(
        select(VideoPromptOutput)
        .join(VideoPromptVersion)
        .join(VideoPrompt)
        .join(VideoProject)
        .where(VideoPromptOutput.id == oid)
        .where(VideoProject.org_id == org.id)
    )
    output = result.scalar_one_or_none()
    if not output:
        raise HTTPException(status_code=404, detail="Output not found")
    return output


def version_to_response(version: VideoPromptVersion) -> VideoPromptVersionResponse:
    """Convert a VideoPromptVersion to response schema."""
    good_count = sum(1 for o in version.outputs if o.rating == "good")
    bad_count = sum(1 for o in version.outputs if o.rating == "bad")
    return VideoPromptVersionResponse(
        id=str(version.id),
        prompt_id=str(version.prompt_id),
        version_number=version.version_number,
        type=version.type,
        status=version.status,
        source_version_id=str(version.source_version_id) if version.source_version_id else None,
        created_by=str(version.created_by) if version.created_by else None,
        created_at=version.created_at.isoformat(),
        scene_description=version.scene_description,
        motion_timing=version.motion_timing,
        style_tone=version.style_tone,
        camera_language=version.camera_language,
        constraints=version.constraints,
        negative_instructions=version.negative_instructions,
        full_prompt_text=version.full_prompt_text,
        output_count=len(version.outputs),
        good_count=good_count,
        bad_count=bad_count,
        score=good_count - bad_count,
    )


# ============================================================================
# Feature Flags Endpoint
# ============================================================================

@router.get("/config/features", response_model=FeatureFlagsResponse)
async def get_feature_flags() -> FeatureFlagsResponse:
    """Get feature flags."""
    return FeatureFlagsResponse(
        video_mvp_enabled=settings.video_mvp_enabled
    )


# ============================================================================
# Video Project Endpoints
# ============================================================================

@router.get("/projects", response_model=VideoProjectListResponse)
async def list_projects(
    org: Organization = Depends(get_current_org_dual),
    db: AsyncSession = Depends(get_db),
) -> VideoProjectListResponse:
    """List all video projects for the current organization."""

    result = await db.execute(
        select(VideoProject)
        .where(VideoProject.org_id == org.id)
        .order_by(desc(VideoProject.updated_at))
    )
    projects = result.scalars().all()

    # Get prompt counts
    project_responses = []
    for project in projects:
        count_result = await db.execute(
            select(func.count(VideoPrompt.id))
            .where(VideoPrompt.project_id == project.id)
        )
        prompt_count = count_result.scalar() or 0
        project_responses.append(VideoProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            created_by=str(project.created_by) if project.created_by else None,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat(),
            prompt_count=prompt_count,
        ))

    logger.info(f"Listed {len(projects)} projects for org {org.id}")
    return VideoProjectListResponse(projects=project_responses, total=len(project_responses))


@router.post("/projects", response_model=VideoProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: CreateVideoProjectRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoProjectResponse:
    """Create a new video project."""
    user_id, org = auth

    project = VideoProject(
        org_id=org.id,
        name=data.name,
        description=data.description,
        created_by=user_id,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)

    logger.info(f"Created project {project.id} by user {user_id}")
    return VideoProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        created_by=str(project.created_by) if project.created_by else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        prompt_count=0,
    )


@router.get("/projects/{project_id}", response_model=VideoProjectResponse)
async def get_project(
    project_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoProjectResponse:
    """Get a video project by ID."""
    user_id, org = auth
    project = await get_project_or_404(project_id, db, org)

    count_result = await db.execute(
        select(func.count(VideoPrompt.id))
        .where(VideoPrompt.project_id == project.id)
    )
    prompt_count = count_result.scalar() or 0

    return VideoProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        created_by=str(project.created_by) if project.created_by else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        prompt_count=prompt_count,
    )


@router.put("/projects/{project_id}", response_model=VideoProjectResponse)
async def update_project(
    project_id: str,
    data: UpdateVideoProjectRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoProjectResponse:
    """Update a video project."""
    user_id, org = auth
    project = await get_project_or_404(project_id, db, org)

    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    project.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(project)

    count_result = await db.execute(
        select(func.count(VideoPrompt.id))
        .where(VideoPrompt.project_id == project.id)
    )
    prompt_count = count_result.scalar() or 0

    logger.info(f"Updated project {project.id} by user {user_id}")
    return VideoProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        created_by=str(project.created_by) if project.created_by else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        prompt_count=prompt_count,
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a video project and all its prompts."""
    user_id, org = auth
    project = await get_project_or_404(project_id, db, org)

    await db.delete(project)
    await db.commit()

    logger.info(f"Deleted project {project_id} by user {user_id}")


# ============================================================================
# Video Prompt Endpoints
# ============================================================================

@router.get("/projects/{project_id}/prompts", response_model=VideoPromptListResponse)
async def list_prompts(
    project_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptListResponse:
    """List all prompts in a project."""
    user_id, org = auth
    project = await get_project_or_404(project_id, db, org)

    result = await db.execute(
        select(VideoPrompt)
        .where(VideoPrompt.project_id == project.id)
        .order_by(desc(VideoPrompt.updated_at))
        .options(selectinload(VideoPrompt.versions))
    )
    prompts = result.scalars().all()

    prompt_responses = []
    for prompt in prompts:
        version_count = len(prompt.versions)
        latest_version = max(prompt.versions, key=lambda v: v.version_number) if prompt.versions else None
        prompt_responses.append(VideoPromptResponse(
            id=str(prompt.id),
            project_id=str(prompt.project_id),
            name=prompt.name,
            purpose=prompt.purpose,
            target_model=prompt.target_model,
            created_by=str(prompt.created_by) if prompt.created_by else None,
            created_at=prompt.created_at.isoformat(),
            updated_at=prompt.updated_at.isoformat(),
            version_count=version_count,
            latest_version_number=latest_version.version_number if latest_version else None,
        ))

    return VideoPromptListResponse(prompts=prompt_responses, total=len(prompt_responses))


@router.post("/projects/{project_id}/prompts", response_model=VideoPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt(
    project_id: str,
    data: CreateVideoPromptRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptResponse:
    """Create a new video prompt with initial version."""
    user_id, org = auth
    project = await get_project_or_404(project_id, db, org)

    # Create prompt
    prompt = VideoPrompt(
        project_id=project.id,
        name=data.name,
        purpose=data.purpose,
        target_model=data.target_model,
        created_by=user_id,
    )
    db.add(prompt)
    await db.flush()

    # Create initial version
    version = VideoPromptVersion(
        prompt_id=prompt.id,
        version_number=1,
        type="main",
        status="active",
        created_by=user_id,
        scene_description=data.scene_description,
        motion_timing=data.motion_timing,
        style_tone=data.style_tone,
        camera_language=data.camera_language,
        constraints=data.constraints,
        negative_instructions=data.negative_instructions,
    )
    version.full_prompt_text = generate_full_prompt_text(version)
    db.add(version)

    await db.commit()
    await db.refresh(prompt)

    logger.info(f"Created prompt {prompt.id} by user {user_id}")
    return VideoPromptResponse(
        id=str(prompt.id),
        project_id=str(prompt.project_id),
        name=prompt.name,
        purpose=prompt.purpose,
        target_model=prompt.target_model,
        created_by=str(prompt.created_by) if prompt.created_by else None,
        created_at=prompt.created_at.isoformat(),
        updated_at=prompt.updated_at.isoformat(),
        version_count=1,
        latest_version_number=1,
    )


@router.get("/prompts/{prompt_id}", response_model=VideoPromptDetailResponse)
async def get_prompt(
    prompt_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptDetailResponse:
    """Get a video prompt with all versions."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    # Load versions with outputs
    result = await db.execute(
        select(VideoPromptVersion)
        .where(VideoPromptVersion.prompt_id == prompt.id)
        .order_by(desc(VideoPromptVersion.version_number))
        .options(selectinload(VideoPromptVersion.outputs))
    )
    versions = result.scalars().all()

    version_responses = [version_to_response(v) for v in versions]

    # Find best version (highest score, tie-break by recency)
    best_version_id = None
    if version_responses:
        scored_versions = [(v, v.score, v.created_at) for v in version_responses]
        scored_versions.sort(key=lambda x: (x[1], x[2]), reverse=True)
        best_version_id = scored_versions[0][0].id if scored_versions[0][1] > 0 else None

    latest_version = max(versions, key=lambda v: v.version_number) if versions else None

    return VideoPromptDetailResponse(
        prompt=VideoPromptResponse(
            id=str(prompt.id),
            project_id=str(prompt.project_id),
            name=prompt.name,
            purpose=prompt.purpose,
            target_model=prompt.target_model,
            created_by=str(prompt.created_by) if prompt.created_by else None,
            created_at=prompt.created_at.isoformat(),
            updated_at=prompt.updated_at.isoformat(),
            version_count=len(versions),
            latest_version_number=latest_version.version_number if latest_version else None,
        ),
        versions=version_responses,
        best_version_id=best_version_id,
    )


@router.put("/prompts/{prompt_id}", response_model=VideoPromptResponse)
async def update_prompt(
    prompt_id: str,
    data: UpdateVideoPromptRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptResponse:
    """Update video prompt metadata."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    if data.name is not None:
        prompt.name = data.name
    if data.purpose is not None:
        prompt.purpose = data.purpose
    if data.target_model is not None:
        prompt.target_model = data.target_model
    prompt.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(prompt)

    logger.info(f"Updated prompt {prompt.id} by user {user_id}")
    return VideoPromptResponse(
        id=str(prompt.id),
        project_id=str(prompt.project_id),
        name=prompt.name,
        purpose=prompt.purpose,
        target_model=prompt.target_model,
        created_by=str(prompt.created_by) if prompt.created_by else None,
        created_at=prompt.created_at.isoformat(),
        updated_at=prompt.updated_at.isoformat(),
        version_count=len(prompt.versions),
        latest_version_number=max(v.version_number for v in prompt.versions) if prompt.versions else None,
    )


@router.delete("/prompts/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prompt(
    prompt_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a video prompt and all its versions."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    await db.delete(prompt)
    await db.commit()

    logger.info(f"Deleted prompt {prompt_id} by user {user_id}")


# ============================================================================
# Version Endpoints
# ============================================================================

@router.post("/prompts/{prompt_id}/versions", response_model=VideoPromptVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    prompt_id: str,
    data: CreateVideoPromptVersionRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptVersionResponse:
    """Create a new version (edit the prompt)."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    # Get next version number
    max_version = max(v.version_number for v in prompt.versions) if prompt.versions else 0

    version = VideoPromptVersion(
        prompt_id=prompt.id,
        version_number=max_version + 1,
        type="main",
        status="active",
        created_by=user_id,
        scene_description=data.scene_description,
        motion_timing=data.motion_timing,
        style_tone=data.style_tone,
        camera_language=data.camera_language,
        constraints=data.constraints,
        negative_instructions=data.negative_instructions,
    )
    version.full_prompt_text = generate_full_prompt_text(version)
    db.add(version)

    prompt.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(version)

    logger.info(f"Created version {version.version_number} for prompt {prompt.id} by user {user_id}")
    return version_to_response(version)


@router.post("/prompts/{prompt_id}/rollback", response_model=VideoPromptVersionResponse)
async def rollback_version(
    prompt_id: str,
    data: RollbackVersionRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptVersionResponse:
    """Rollback to a specific version by creating a new version with that content."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    # Get the target version
    target = await get_version_or_404(data.version_id, db, user)
    if target.prompt_id != prompt.id:
        raise HTTPException(status_code=400, detail="Version does not belong to this prompt")

    # Get next version number
    max_version = max(v.version_number for v in prompt.versions) if prompt.versions else 0

    # Create new version with target's content
    version = VideoPromptVersion(
        prompt_id=prompt.id,
        version_number=max_version + 1,
        type="main",
        status="active",
        source_version_id=target.id,
        created_by=user_id,
        scene_description=target.scene_description,
        motion_timing=target.motion_timing,
        style_tone=target.style_tone,
        camera_language=target.camera_language,
        constraints=target.constraints,
        negative_instructions=target.negative_instructions,
        full_prompt_text=target.full_prompt_text,
    )
    db.add(version)

    prompt.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(version)

    logger.info(f"Rolled back prompt {prompt.id} to version {target.version_number} by user {user_id}")
    return version_to_response(version)


@router.post("/prompts/{prompt_id}/generate-variants", response_model=VideoPromptVersionListResponse)
async def generate_variants(
    prompt_id: str,
    data: GenerateVariantsRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptVersionListResponse:
    """Generate prompt variants using LLM."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    # Get the latest version
    if not prompt.versions:
        raise HTTPException(status_code=400, detail="Prompt has no versions")

    latest = max(prompt.versions, key=lambda v: v.version_number)

    # Extract version data before passing to variant generator to avoid async context issues
    version_data = {
        "id": latest.id,
        "scene_description": latest.scene_description,
        "motion_timing": latest.motion_timing,
        "style_tone": latest.style_tone,
        "camera_language": latest.camera_language,
        "constraints": latest.constraints,
        "negative_instructions": latest.negative_instructions,
    }

    # Import the variant generator
    from ..services.video_variant_generator import generate_prompt_variants

    try:
        variants_data = await generate_prompt_variants(version_data, data.count)
    except Exception as e:
        logger.error(f"Failed to generate variants: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate variants: {str(e)}")

    # Create variant versions
    max_version = max(v.version_number for v in prompt.versions) if prompt.versions else 0
    created_versions = []

    for i, variant in enumerate(variants_data):
        version = VideoPromptVersion(
            prompt_id=prompt.id,
            version_number=max_version + i + 1,
            type="variant",
            status="draft",
            source_version_id=latest.id,
            created_by=user_id,
            scene_description=variant.get("scene_description"),
            motion_timing=variant.get("motion_timing"),
            style_tone=variant.get("style_tone"),
            camera_language=variant.get("camera_language"),
            constraints=variant.get("constraints"),
            negative_instructions=variant.get("negative_instructions"),
        )
        version.full_prompt_text = generate_full_prompt_text(version)
        db.add(version)
        created_versions.append(version)

    prompt.updated_at = datetime.utcnow()

    await db.commit()

    # Reload versions with outputs to avoid lazy loading issues
    version_ids = [v.id for v in created_versions]
    result = await db.execute(
        select(VideoPromptVersion)
        .where(VideoPromptVersion.id.in_(version_ids))
        .options(selectinload(VideoPromptVersion.outputs))
    )
    loaded_versions = result.scalars().all()

    logger.info(f"Generated {len(loaded_versions)} variants for prompt {prompt.id} by user {user_id}")
    return VideoPromptVersionListResponse(
        versions=[version_to_response(v) for v in loaded_versions],
        total=len(loaded_versions),
    )


@router.post("/versions/{version_id}/promote", response_model=VideoPromptVersionResponse)
async def promote_variant(
    version_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptVersionResponse:
    """Promote a draft variant to an active main version."""
    user_id, org = auth
    version = await get_version_or_404(version_id, db, org)

    if version.type != "variant" or version.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft variants can be promoted")

    version.type = "main"
    version.status = "active"

    await db.commit()
    await db.refresh(version)

    logger.info(f"Promoted variant {version.id} to main by user {user_id}")
    return version_to_response(version)


@router.delete("/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(
    version_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a draft variant version."""
    user_id, org = auth
    version = await get_version_or_404(version_id, db, org)

    if version.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft versions can be deleted")

    await db.delete(version)
    await db.commit()

    logger.info(f"Deleted version {version_id} by user {user_id}")


# ============================================================================
# Output Endpoints
# ============================================================================

@router.post("/versions/{version_id}/outputs", response_model=VideoPromptOutputResponse, status_code=status.HTTP_201_CREATED)
async def attach_output(
    version_id: str,
    data: AttachOutputRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptOutputResponse:
    """Attach an output to a version."""
    user_id, org = auth
    version = await get_version_or_404(version_id, db, org)

    output = VideoPromptOutput(
        version_id=version.id,
        created_by=user_id,
        url=data.url,
        notes=data.notes,
    )
    db.add(output)
    await db.commit()
    await db.refresh(output)

    logger.info(f"Attached output {output.id} to version {version.id} by user {user_id}")
    return VideoPromptOutputResponse(
        id=str(output.id),
        version_id=str(output.version_id),
        created_by=str(output.created_by) if output.created_by else None,
        created_at=output.created_at.isoformat(),
        url=output.url,
        notes=output.notes,
        rating=output.rating,
        reason_tags=output.reason_tags,
    )


@router.get("/versions/{version_id}/outputs", response_model=VideoPromptOutputListResponse)
async def list_outputs(
    version_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptOutputListResponse:
    """List all outputs for a version."""
    user_id, org = auth
    version = await get_version_or_404(version_id, db, org)

    result = await db.execute(
        select(VideoPromptOutput)
        .where(VideoPromptOutput.version_id == version.id)
        .order_by(desc(VideoPromptOutput.created_at))
    )
    outputs = result.scalars().all()

    return VideoPromptOutputListResponse(
        outputs=[
            VideoPromptOutputResponse(
                id=str(o.id),
                version_id=str(o.version_id),
                created_by=str(o.created_by) if o.created_by else None,
                created_at=o.created_at.isoformat(),
                url=o.url,
                notes=o.notes,
                rating=o.rating,
                reason_tags=o.reason_tags,
            )
            for o in outputs
        ],
        total=len(outputs),
    )


@router.put("/outputs/{output_id}/score", response_model=VideoPromptOutputResponse)
async def score_output(
    output_id: str,
    data: ScoreOutputRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptOutputResponse:
    """Score an output."""
    user_id, org = auth
    output = await get_output_or_404(output_id, db, org)

    output.rating = data.rating
    output.reason_tags = data.reason_tags

    await db.commit()
    await db.refresh(output)

    logger.info(f"Scored output {output.id} as {data.rating} by user {user_id}")
    return VideoPromptOutputResponse(
        id=str(output.id),
        version_id=str(output.version_id),
        created_by=str(output.created_by) if output.created_by else None,
        created_at=output.created_at.isoformat(),
        url=output.url,
        notes=output.notes,
        rating=output.rating,
        reason_tags=output.reason_tags,
    )


@router.delete("/outputs/{output_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output(
    output_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an output."""
    user_id, org = auth
    output = await get_output_or_404(output_id, db, org)

    await db.delete(output)
    await db.commit()

    logger.info(f"Deleted output {output_id} by user {user_id}")


# ============================================================================
# Best Version Endpoint
# ============================================================================

@router.get("/prompts/{prompt_id}/best", response_model=VideoPromptVersionResponse)
async def get_best_version(
    prompt_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> VideoPromptVersionResponse:
    """Get the best performing version for a prompt."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    # Load versions with outputs
    result = await db.execute(
        select(VideoPromptVersion)
        .where(VideoPromptVersion.prompt_id == prompt.id)
        .options(selectinload(VideoPromptVersion.outputs))
    )
    versions = result.scalars().all()

    if not versions:
        raise HTTPException(status_code=404, detail="No versions found")

    # Calculate scores
    version_scores = []
    for v in versions:
        good_count = sum(1 for o in v.outputs if o.rating == "good")
        bad_count = sum(1 for o in v.outputs if o.rating == "bad")
        score = good_count - bad_count
        version_scores.append((v, score, v.created_at))

    # Sort by score desc, then by created_at desc
    version_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
    best = version_scores[0][0]

    return version_to_response(best)


# ============================================================================
# Share Token Endpoints
# ============================================================================

@router.post("/prompts/{prompt_id}/share", response_model=ShareTokenResponse, status_code=status.HTTP_201_CREATED)
async def create_share_token(
    prompt_id: str,
    data: CreateShareTokenRequest,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ShareTokenResponse:
    """Create a share token for a prompt."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    # Generate token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()

    share_token = VideoPromptShareToken(
        prompt_id=prompt.id,
        token_hash=token_hash,
        created_by=user_id,
        expires_at=datetime.utcnow() + timedelta(days=data.expires_in_days),
    )
    db.add(share_token)
    await db.commit()
    await db.refresh(share_token)

    logger.info(f"Created share token for prompt {prompt.id} by user {user_id}")
    return ShareTokenResponse(
        id=str(share_token.id),
        prompt_id=str(share_token.prompt_id),
        token=raw_token,  # Only returned on creation
        created_by=str(share_token.created_by) if share_token.created_by else None,
        created_at=share_token.created_at.isoformat(),
        expires_at=share_token.expires_at.isoformat(),
        revoked_at=share_token.revoked_at.isoformat() if share_token.revoked_at else None,
        is_active=share_token.revoked_at is None and share_token.expires_at > datetime.utcnow(),
    )


@router.get("/prompts/{prompt_id}/shares", response_model=ShareTokenListResponse)
async def list_share_tokens(
    prompt_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> ShareTokenListResponse:
    """List all share tokens for a prompt."""
    user_id, org = auth
    prompt = await get_prompt_or_404(prompt_id, db, org)

    result = await db.execute(
        select(VideoPromptShareToken)
        .where(VideoPromptShareToken.prompt_id == prompt.id)
        .order_by(desc(VideoPromptShareToken.created_at))
    )
    tokens = result.scalars().all()

    now = datetime.utcnow()
    return ShareTokenListResponse(
        tokens=[
            ShareTokenResponse(
                id=str(t.id),
                prompt_id=str(t.prompt_id),
                token=None,  # Never expose existing tokens
                created_by=str(t.created_by) if t.created_by else None,
                created_at=t.created_at.isoformat(),
                expires_at=t.expires_at.isoformat(),
                revoked_at=t.revoked_at.isoformat() if t.revoked_at else None,
                is_active=t.revoked_at is None and t.expires_at > now,
            )
            for t in tokens
        ],
        total=len(tokens),
    )


@router.delete("/shares/{share_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_share_token(
    share_id: str,
    auth: tuple[Optional[uuid.UUID], Organization] = Depends(get_auth_context),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Revoke a share token."""
    user_id, org = auth

    try:
        sid = uuid.UUID(share_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid share token ID")

    result = await db.execute(
        select(VideoPromptShareToken)
        .join(VideoPrompt)
        .join(VideoProject)
        .where(VideoPromptShareToken.id == sid)
        .where(VideoProject.org_id == org.id)
    )
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(status_code=404, detail="Share token not found")

    token.revoked_at = datetime.utcnow()
    await db.commit()

    logger.info(f"Revoked share token {share_id} by user {user_id}")


# ============================================================================
# Public Share Endpoint (No Auth Required)
# ============================================================================

@router.get("/share/{token}", response_model=SharedVideoPromptResponse)
async def get_shared_prompt(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> SharedVideoPromptResponse:
    """Get a prompt via share token (public read-only access)."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    result = await db.execute(
        select(VideoPromptShareToken)
        .where(VideoPromptShareToken.token_hash == token_hash)
        .options(selectinload(VideoPromptShareToken.prompt))
    )
    share_token = result.scalar_one_or_none()

    if not share_token:
        raise HTTPException(status_code=404, detail="Invalid share link")

    now = datetime.utcnow()
    if share_token.revoked_at is not None:
        raise HTTPException(status_code=403, detail="This share link has been revoked")
    if share_token.expires_at < now:
        raise HTTPException(status_code=403, detail="This share link has expired")

    prompt = share_token.prompt

    # Load versions with outputs
    result = await db.execute(
        select(VideoPromptVersion)
        .where(VideoPromptVersion.prompt_id == prompt.id)
        .order_by(desc(VideoPromptVersion.version_number))
        .options(selectinload(VideoPromptVersion.outputs))
    )
    versions = result.scalars().all()

    version_responses = [version_to_response(v) for v in versions]

    # Collect all outputs
    all_outputs = []
    for v in versions:
        for o in v.outputs:
            all_outputs.append(VideoPromptOutputResponse(
                id=str(o.id),
                version_id=str(o.version_id),
                created_by=str(o.created_by) if o.created_by else None,
                created_at=o.created_at.isoformat(),
                url=o.url,
                notes=o.notes,
                rating=o.rating,
                reason_tags=o.reason_tags,
            ))

    # Find best version
    best_version_id = None
    if version_responses:
        scored_versions = [(v, v.score, v.created_at) for v in version_responses]
        scored_versions.sort(key=lambda x: (x[1], x[2]), reverse=True)
        best_version_id = scored_versions[0][0].id if scored_versions[0][1] > 0 else None

    latest_version = max(versions, key=lambda v: v.version_number) if versions else None

    logger.info(f"Accessed shared prompt {prompt.id} via token")
    return SharedVideoPromptResponse(
        prompt=VideoPromptResponse(
            id=str(prompt.id),
            project_id=str(prompt.project_id),
            name=prompt.name,
            purpose=prompt.purpose,
            target_model=prompt.target_model,
            created_by=None,  # Hide creator in shared view
            created_at=prompt.created_at.isoformat(),
            updated_at=prompt.updated_at.isoformat(),
            version_count=len(versions),
            latest_version_number=latest_version.version_number if latest_version else None,
        ),
        versions=version_responses,
        outputs=all_outputs,
        best_version_id=best_version_id,
    )
