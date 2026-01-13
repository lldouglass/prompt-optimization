"""Video workflow models for the 7-step wizard."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING:
    from .organization import Organization
    from .user import User


class VideoWorkflow(Base):
    """A video workflow containing all 7 steps of the wizard.

    Steps:
    1. Brief Intake
    2. Clarifying Questions
    3. Continuity Pack
    4. Shot Plan
    5. Prompt Pack (Sora 2)
    6. QA Score + Fix Suggestions
    7. Export / Save / Reuse
    """
    __tablename__ = "video_workflows"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Workflow state
    current_step: Mapped[int] = mapped_column(Integer, default=1)  # 1-7
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, in_progress, completed

    # Template support
    is_template: Mapped[bool] = mapped_column(Boolean, default=False)
    template_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_template_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("video_workflows.id", ondelete="SET NULL"), nullable=True
    )

    # Step 1-2: Brief Intake + Clarifying Questions
    # Structure:
    # {
    #   "project_name": str,
    #   "goal": "product_ad" | "ugc" | "explainer" | "cinematic_brand" | "tutorial" | "other",
    #   "platform": "tiktok" | "instagram" | "youtube" | "web" | "other",
    #   "aspect_ratio": "9:16" | "1:1" | "16:9",
    #   "duration_seconds": int,
    #   "brand_vibe": [str, str, str],
    #   "avoid_vibe": [str, str, str],
    #   "must_include": [str],
    #   "must_avoid": [str],
    #   "script_or_vo": str | null,
    #   "product_or_subject_description": str,
    #   "reference_images": [str] | null,
    #   "clarifying_questions": [
    #     {"id": str, "question": str, "category": str, "answer": str | null}
    #   ]
    # }
    brief: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Step 3: Continuity Pack
    # Structure:
    # {
    #   "anchors": [{"type": str, "description": str}],
    #   "lighting_recipe": {
    #     "key_light": str,
    #     "fill_light": str,
    #     "rim_light": str,
    #     "softness": str,
    #     "time_of_day": str
    #   },
    #   "palette_anchors": [{"name": str, "hex": str}],
    #   "do_list": [str],
    #   "dont_list": [str],
    #   "style_clause": str
    # }
    continuity_pack: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Step 4: Shot Plan
    # Structure:
    # {
    #   "shots": [
    #     {
    #       "id": str,
    #       "shot_number": int,
    #       "start_sec": float,
    #       "end_sec": float,
    #       "shot_type": "wide" | "medium" | "close" | "detail",
    #       "camera_move": "none" | "pan" | "tilt" | "orbit" | "push_in" | "pull_out" | "crane",
    #       "framing_notes": str,
    #       "subject_action_beats": [str],
    #       "setting_notes": str,
    #       "audio_cue": str | null,
    #       "purpose": str
    #     }
    #   ]
    # }
    shot_plan: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Step 5: Prompt Pack (Sora 2)
    # Structure:
    # {
    #   "target_model": "sora_2",
    #   "prompts": [
    #     {
    #       "shot_id": str,
    #       "sora_params": {"resolution": str, "duration": float, "aspect_ratio": str},
    #       "prompt_text": str,
    #       "negative_prompt_text": str | null,
    #       "dialogue_block": str | null
    #     }
    #   ]
    # }
    prompt_pack: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Step 6: QA Score
    # Structure:
    # {
    #   "ambiguity_risk": int (0-100),
    #   "motion_complexity_risk": int (0-100),
    #   "continuity_completeness": int (0-100),
    #   "audio_readiness": int (0-100),
    #   "overall_score": int (0-100),
    #   "warnings": [str],
    #   "fixes": [{"issue": str, "fix": str}],
    #   "recommended_questions": [str]
    # }
    qa_score: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Step 7: Versions (for save/restore)
    # Structure:
    # [
    #   {
    #     "version_number": int,
    #     "step": str,  # "brief", "continuity", "shots", "prompts"
    #     "data": {...},
    #     "created_at": str (ISO datetime)
    #   }
    # ]
    versions: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    # Metadata
    created_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_video_workflows_org_status", "org_id", "status"),
        Index("idx_video_workflows_org_template", "org_id", "is_template"),
        Index("idx_video_workflows_org_created", "org_id", "created_at"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="video_workflows")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    source_template: Mapped["VideoWorkflow | None"] = relationship(
        remote_side=[id], foreign_keys=[source_template_id]
    )


# Helper functions for working with workflow data

def get_brief_project_name(workflow: VideoWorkflow) -> str:
    """Get the project name from the brief, or workflow name as fallback."""
    if workflow.brief and workflow.brief.get("project_name"):
        return workflow.brief["project_name"]
    return workflow.name


def get_total_duration(workflow: VideoWorkflow) -> float:
    """Get total duration from brief or shot plan."""
    if workflow.brief and workflow.brief.get("duration_seconds"):
        return float(workflow.brief["duration_seconds"])
    if workflow.shot_plan and workflow.shot_plan.get("shots"):
        shots = workflow.shot_plan["shots"]
        if shots:
            return max(shot.get("end_sec", 0) for shot in shots)
    return 0.0


def get_shot_count(workflow: VideoWorkflow) -> int:
    """Get number of shots in the shot plan."""
    if workflow.shot_plan and workflow.shot_plan.get("shots"):
        return len(workflow.shot_plan["shots"])
    return 0


def get_prompt_count(workflow: VideoWorkflow) -> int:
    """Get number of prompts in the prompt pack."""
    if workflow.prompt_pack and workflow.prompt_pack.get("prompts"):
        return len(workflow.prompt_pack["prompts"])
    return 0
