"""Schemas for video prompt optimization endpoints."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ============================================================================
# Video Project Schemas
# ============================================================================

class CreateVideoProjectRequest(BaseModel):
    """Request to create a new video project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Optional project description")


class UpdateVideoProjectRequest(BaseModel):
    """Request to update a video project."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class VideoProjectResponse(BaseModel):
    """Response containing a video project."""
    id: str
    name: str
    description: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str
    updated_at: str
    prompt_count: int = 0


class VideoProjectListResponse(BaseModel):
    """Response containing list of video projects."""
    projects: list[VideoProjectResponse]
    total: int


# ============================================================================
# Video Prompt Schemas
# ============================================================================

class CreateVideoPromptRequest(BaseModel):
    """Request to create a new video prompt."""
    name: str = Field(..., min_length=1, max_length=255, description="Prompt name")
    purpose: Optional[str] = Field(None, max_length=2000, description="Purpose/goal of the prompt")
    target_model: Optional[str] = Field(None, max_length=100, description="Target video model (e.g., Runway, Pika)")
    # Initial version content
    scene_description: Optional[str] = Field(None, description="Scene description")
    motion_timing: Optional[str] = Field(None, description="Motion and timing instructions")
    style_tone: Optional[str] = Field(None, description="Style and tone")
    camera_language: Optional[str] = Field(None, description="Camera language/movement")
    constraints: Optional[str] = Field(None, description="Constraints and requirements")
    negative_instructions: Optional[str] = Field(None, description="What to avoid")


class UpdateVideoPromptRequest(BaseModel):
    """Request to update video prompt metadata (not content - that creates a new version)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    purpose: Optional[str] = Field(None, max_length=2000)
    target_model: Optional[str] = Field(None, max_length=100)


class VideoPromptResponse(BaseModel):
    """Response containing a video prompt (without versions)."""
    id: str
    project_id: str
    name: str
    purpose: Optional[str] = None
    target_model: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str
    updated_at: str
    version_count: int = 0
    latest_version_number: Optional[int] = None


class VideoPromptListResponse(BaseModel):
    """Response containing list of video prompts."""
    prompts: list[VideoPromptResponse]
    total: int


# ============================================================================
# Video Prompt Version Schemas
# ============================================================================

class CreateVideoPromptVersionRequest(BaseModel):
    """Request to create a new version (edit the prompt)."""
    scene_description: Optional[str] = Field(None, description="Scene description")
    motion_timing: Optional[str] = Field(None, description="Motion and timing instructions")
    style_tone: Optional[str] = Field(None, description="Style and tone")
    camera_language: Optional[str] = Field(None, description="Camera language/movement")
    constraints: Optional[str] = Field(None, description="Constraints and requirements")
    negative_instructions: Optional[str] = Field(None, description="What to avoid")


class RollbackVersionRequest(BaseModel):
    """Request to rollback to a specific version."""
    version_id: str = Field(..., description="ID of the version to rollback to")


class PromoteVariantRequest(BaseModel):
    """Request to promote a variant to a main version."""
    version_id: str = Field(..., description="ID of the variant version to promote")


class GenerateVariantsRequest(BaseModel):
    """Request to generate prompt variants."""
    count: int = Field(5, ge=1, le=10, description="Number of variants to generate (1-10)")


class VideoPromptVersionResponse(BaseModel):
    """Response containing a video prompt version."""
    id: str
    prompt_id: str
    version_number: int
    type: str  # 'main' or 'variant'
    status: str  # 'active' or 'draft'
    source_version_id: Optional[str] = None
    created_by: Optional[str] = None
    created_at: str
    # Structured fields
    scene_description: Optional[str] = None
    motion_timing: Optional[str] = None
    style_tone: Optional[str] = None
    camera_language: Optional[str] = None
    constraints: Optional[str] = None
    negative_instructions: Optional[str] = None
    full_prompt_text: Optional[str] = None
    # Computed fields
    output_count: int = 0
    good_count: int = 0
    bad_count: int = 0
    score: int = 0  # good_count - bad_count


class VideoPromptVersionListResponse(BaseModel):
    """Response containing list of versions."""
    versions: list[VideoPromptVersionResponse]
    total: int


# ============================================================================
# Video Prompt Output Schemas
# ============================================================================

class AttachOutputRequest(BaseModel):
    """Request to attach an output to a version."""
    url: str = Field(..., min_length=1, description="URL of the video output")
    notes: Optional[str] = Field(None, max_length=2000, description="Optional notes about the output")


class ScoreOutputRequest(BaseModel):
    """Request to score an output."""
    rating: str = Field(..., pattern="^(good|bad)$", description="Rating: 'good' or 'bad'")
    reason_tags: Optional[list[str]] = Field(
        None,
        description="Reason tags (e.g., 'flicker', 'character_drift', 'too_fast', 'artifacting', 'off_brand', 'other')"
    )


class VideoPromptOutputResponse(BaseModel):
    """Response containing a video output."""
    id: str
    version_id: str
    created_by: Optional[str] = None
    created_at: str
    url: str
    notes: Optional[str] = None
    rating: Optional[str] = None
    reason_tags: Optional[list[str]] = None


class VideoPromptOutputListResponse(BaseModel):
    """Response containing list of outputs."""
    outputs: list[VideoPromptOutputResponse]
    total: int


# ============================================================================
# Share Token Schemas
# ============================================================================

class CreateShareTokenRequest(BaseModel):
    """Request to create a share token."""
    expires_in_days: int = Field(7, ge=1, le=30, description="Token expiration in days (1-30)")


class ShareTokenResponse(BaseModel):
    """Response containing a share token."""
    id: str
    prompt_id: str
    token: Optional[str] = None  # Only included on creation
    created_by: Optional[str] = None
    created_at: str
    expires_at: str
    revoked_at: Optional[str] = None
    is_active: bool


class ShareTokenListResponse(BaseModel):
    """Response containing list of share tokens."""
    tokens: list[ShareTokenResponse]
    total: int


# ============================================================================
# Detail/Combined Schemas
# ============================================================================

class VideoPromptDetailResponse(BaseModel):
    """Detailed response for a video prompt including versions and outputs."""
    prompt: VideoPromptResponse
    versions: list[VideoPromptVersionResponse]
    best_version_id: Optional[str] = None
    share_url: Optional[str] = None


class SharedVideoPromptResponse(BaseModel):
    """Response for shared read-only view of a video prompt."""
    prompt: VideoPromptResponse
    versions: list[VideoPromptVersionResponse]
    outputs: list[VideoPromptOutputResponse]
    best_version_id: Optional[str] = None


# ============================================================================
# Feature Flags Schema
# ============================================================================

class FeatureFlagsResponse(BaseModel):
    """Response containing feature flags."""
    video_mvp_enabled: bool
