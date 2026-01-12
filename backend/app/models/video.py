"""Video prompt optimization models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base

if TYPE_CHECKING:
    from .organization import Organization
    from .user import User


class VideoProject(Base):
    """A project containing video prompts."""
    __tablename__ = "video_projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="video_projects")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    prompts: Mapped[list["VideoPrompt"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class VideoPrompt(Base):
    """A video prompt within a project."""
    __tablename__ = "video_prompts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("video_projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project: Mapped["VideoProject"] = relationship(back_populates="prompts")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    versions: Mapped[list["VideoPromptVersion"]] = relationship(back_populates="prompt", cascade="all, delete-orphan")
    share_tokens: Mapped[list["VideoPromptShareToken"]] = relationship(back_populates="prompt", cascade="all, delete-orphan")


class VideoPromptVersion(Base):
    """An immutable version of a video prompt."""
    __tablename__ = "video_prompt_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("video_prompts.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="main")  # 'main' or 'variant'
    status: Mapped[str] = mapped_column(String(20), default="active")  # 'active' or 'draft'
    source_version_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("video_prompt_versions.id", ondelete="SET NULL"), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Structured prompt fields
    scene_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    motion_timing: Mapped[str | None] = mapped_column(Text, nullable=True)
    style_tone: Mapped[str | None] = mapped_column(Text, nullable=True)
    camera_language: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    negative_instructions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Generated full prompt text
    full_prompt_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    prompt: Mapped["VideoPrompt"] = relationship(back_populates="versions")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    source_version: Mapped["VideoPromptVersion | None"] = relationship(remote_side=[id], foreign_keys=[source_version_id])
    outputs: Mapped[list["VideoPromptOutput"]] = relationship(back_populates="version", cascade="all, delete-orphan")


class VideoPromptOutput(Base):
    """An output (video link) attached to a prompt version with optional rating."""
    __tablename__ = "video_prompt_outputs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("video_prompt_versions.id", ondelete="CASCADE"))
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Output data
    url: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Rating (null = not rated, 'good' or 'bad')
    rating: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reason_tags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # e.g., ["flicker", "character_drift"]

    # Relationships
    version: Mapped["VideoPromptVersion"] = relationship(back_populates="outputs")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])


class VideoPromptShareToken(Base):
    """A shareable read-only access token for a video prompt."""
    __tablename__ = "video_prompt_share_tokens"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("video_prompts.id", ondelete="CASCADE"))
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    prompt: Mapped["VideoPrompt"] = relationship(back_populates="share_tokens")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])


def generate_full_prompt_text(version: VideoPromptVersion) -> str:
    """Generate the full prompt text from structured fields."""
    parts = []
    if version.scene_description:
        parts.append(f"Scene: {version.scene_description}")
    if version.motion_timing:
        parts.append(f"Motion/Timing: {version.motion_timing}")
    if version.style_tone:
        parts.append(f"Style/Tone: {version.style_tone}")
    if version.camera_language:
        parts.append(f"Camera: {version.camera_language}")
    if version.constraints:
        parts.append(f"Constraints: {version.constraints}")
    if version.negative_instructions:
        parts.append(f"Avoid: {version.negative_instructions}")
    return "\n\n".join(parts)
