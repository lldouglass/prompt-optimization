"""Pydantic schemas for video workflow API."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class WorkflowGoal(str, Enum):
    PRODUCT_AD = "product_ad"
    UGC = "ugc"
    EXPLAINER = "explainer"
    CINEMATIC_BRAND = "cinematic_brand"
    TUTORIAL = "tutorial"
    OTHER = "other"


class WorkflowPlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE = "youtube"
    WEB = "web"
    OTHER = "other"


class AspectRatio(str, Enum):
    PORTRAIT = "9:16"
    SQUARE = "1:1"
    LANDSCAPE = "16:9"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ShotType(str, Enum):
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE = "close"
    DETAIL = "detail"


class CameraMove(str, Enum):
    NONE = "none"
    PAN = "pan"
    TILT = "tilt"
    ORBIT = "orbit"
    PUSH_IN = "push_in"
    PULL_OUT = "pull_out"
    CRANE = "crane"


class QuestionCategory(str, Enum):
    SHOT_STYLE = "shot_style"
    PACING = "pacing"
    CAMERA_MOVEMENT = "camera_movement"
    ACTION_BEATS = "action_beats"
    AUDIO = "audio"
    CTA = "cta"


class ExportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"


# ============================================================================
# Brief Intake (Steps 1-2)
# ============================================================================

class ClarifyingQuestion(BaseModel):
    """A clarifying question generated for the user."""
    id: str
    question: str
    category: QuestionCategory
    answer: Optional[str] = None


class BriefIntakeRequest(BaseModel):
    """Request to save/update brief intake data."""
    project_name: str = Field(..., min_length=1, max_length=255)
    goal: WorkflowGoal
    platform: WorkflowPlatform
    aspect_ratio: AspectRatio
    duration_seconds: int = Field(..., ge=3, le=180)
    brand_vibe: list[str] = Field(..., min_length=1, max_length=3)
    avoid_vibe: list[str] = Field(default_factory=list, max_length=3)
    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)
    script_or_vo: Optional[str] = None
    product_or_subject_description: str = Field(..., min_length=1, max_length=2000)
    reference_images: Optional[list[str]] = None


class AnswerQuestionsRequest(BaseModel):
    """Request to submit answers to clarifying questions."""
    answers: dict[str, str]  # question_id -> answer


class BriefData(BaseModel):
    """Full brief data including Q&A."""
    project_name: str
    goal: WorkflowGoal
    platform: WorkflowPlatform
    aspect_ratio: AspectRatio
    duration_seconds: int
    brand_vibe: list[str]
    avoid_vibe: list[str]
    must_include: list[str]
    must_avoid: list[str]
    script_or_vo: Optional[str] = None
    product_or_subject_description: str
    reference_images: Optional[list[str]] = None
    clarifying_questions: list[ClarifyingQuestion] = Field(default_factory=list)


# ============================================================================
# Continuity Pack (Step 3)
# ============================================================================

class Anchor(BaseModel):
    """A visual anchor for continuity."""
    type: str  # character, product, wardrobe, props, environment
    description: str


class LightingRecipe(BaseModel):
    """Lighting recipe for consistency."""
    key_light: str
    fill_light: str
    rim_light: Optional[str] = None
    softness: str
    time_of_day: str


class PaletteAnchor(BaseModel):
    """Color palette anchor."""
    name: str
    hex: str


class ContinuityPackData(BaseModel):
    """Full continuity pack data."""
    anchors: list[Anchor] = Field(default_factory=list)
    lighting_recipe: Optional[LightingRecipe] = None
    palette_anchors: list[PaletteAnchor] = Field(default_factory=list)
    do_list: list[str] = Field(default_factory=list)
    dont_list: list[str] = Field(default_factory=list)
    style_clause: Optional[str] = None


class UpdateContinuityRequest(BaseModel):
    """Request to update continuity pack."""
    anchors: Optional[list[Anchor]] = None
    lighting_recipe: Optional[LightingRecipe] = None
    palette_anchors: Optional[list[PaletteAnchor]] = None
    do_list: Optional[list[str]] = None
    dont_list: Optional[list[str]] = None
    style_clause: Optional[str] = None


# ============================================================================
# Shot Plan (Step 4)
# ============================================================================

class ShotData(BaseModel):
    """A single shot in the shot plan."""
    id: str
    shot_number: int
    start_sec: float
    end_sec: float
    shot_type: ShotType
    camera_move: CameraMove
    framing_notes: str
    subject_action_beats: list[str] = Field(default_factory=list, max_length=5)
    setting_notes: str
    audio_cue: Optional[str] = None
    purpose: str


class ShotPlanData(BaseModel):
    """Full shot plan data."""
    shots: list[ShotData] = Field(default_factory=list)


class UpdateShotRequest(BaseModel):
    """Request to update a single shot."""
    shot_type: Optional[ShotType] = None
    camera_move: Optional[CameraMove] = None
    framing_notes: Optional[str] = None
    subject_action_beats: Optional[list[str]] = None
    setting_notes: Optional[str] = None
    audio_cue: Optional[str] = None
    purpose: Optional[str] = None
    start_sec: Optional[float] = None
    end_sec: Optional[float] = None


# ============================================================================
# Prompt Pack (Step 5)
# ============================================================================

class SoraParams(BaseModel):
    """Sora 2 API parameters."""
    resolution: str = "1080p"
    duration: float
    aspect_ratio: str
    fps: int = 24
    seed: Optional[int] = None


class ShotPromptData(BaseModel):
    """A compiled prompt for a single shot."""
    shot_id: str
    sora_params: SoraParams
    prompt_text: str
    negative_prompt_text: Optional[str] = None
    dialogue_block: Optional[str] = None


class PromptPackData(BaseModel):
    """Full prompt pack data."""
    target_model: str = "sora_2"
    prompts: list[ShotPromptData] = Field(default_factory=list)


class UpdatePromptRequest(BaseModel):
    """Request to update a single prompt."""
    prompt_text: Optional[str] = None
    negative_prompt_text: Optional[str] = None
    dialogue_block: Optional[str] = None
    sora_params: Optional[SoraParams] = None


class GeneratePromptsRequest(BaseModel):
    """Request to generate prompts for a target model."""
    target_model: str = "sora_2"


# ============================================================================
# QA Score (Step 6)
# ============================================================================

class QAFix(BaseModel):
    """A suggested fix for a QA issue."""
    issue: str
    fix: str


class QAScoreData(BaseModel):
    """QA scoring results."""
    ambiguity_risk: int = Field(..., ge=0, le=100)
    motion_complexity_risk: int = Field(..., ge=0, le=100)
    continuity_completeness: int = Field(..., ge=0, le=100)
    audio_readiness: int = Field(..., ge=0, le=100)
    overall_score: int = Field(..., ge=0, le=100)
    warnings: list[str] = Field(default_factory=list)
    fixes: list[QAFix] = Field(default_factory=list)
    recommended_questions: list[str] = Field(default_factory=list)


# ============================================================================
# Versions (Step 7)
# ============================================================================

class VersionSnapshot(BaseModel):
    """A version snapshot of workflow data."""
    version_number: int
    step: str  # brief, continuity, shots, prompts
    data: dict
    created_at: str


class SaveVersionRequest(BaseModel):
    """Request to save a version snapshot."""
    step: str  # brief, continuity, shots, prompts


class CreateTemplateRequest(BaseModel):
    """Request to create a template from a workflow."""
    template_name: str = Field(..., min_length=1, max_length=255)


class CreateFromTemplateRequest(BaseModel):
    """Request to create a workflow from a template."""
    name: str = Field(..., min_length=1, max_length=255)


# ============================================================================
# Workflow CRUD
# ============================================================================

class CreateVideoWorkflowRequest(BaseModel):
    """Request to create a new video workflow."""
    name: str = Field(..., min_length=1, max_length=255)


class VideoWorkflowResponse(BaseModel):
    """Response containing a video workflow summary."""
    id: str
    name: str
    current_step: int
    status: WorkflowStatus
    is_template: bool
    template_name: Optional[str] = None
    shot_count: int = 0
    prompt_count: int = 0
    overall_score: Optional[int] = None
    created_by: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


class VideoWorkflowDetailResponse(BaseModel):
    """Response containing full video workflow details."""
    id: str
    name: str
    current_step: int
    status: WorkflowStatus
    is_template: bool
    template_name: Optional[str] = None
    source_template_id: Optional[str] = None

    # Step data
    brief: Optional[BriefData] = None
    continuity_pack: Optional[ContinuityPackData] = None
    shot_plan: Optional[ShotPlanData] = None
    prompt_pack: Optional[PromptPackData] = None
    qa_score: Optional[QAScoreData] = None
    versions: list[VersionSnapshot] = Field(default_factory=list)

    created_by: Optional[str] = None
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


# ============================================================================
# Export
# ============================================================================

class ExportWorkflowRequest(BaseModel):
    """Request to export a workflow."""
    format: ExportFormat = ExportFormat.JSON


class ExportWorkflowResponse(BaseModel):
    """Response containing exported workflow data."""
    format: ExportFormat
    filename: str
    content: str  # JSON string or Markdown
