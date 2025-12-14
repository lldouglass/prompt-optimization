import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Float, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class PromptOptimization(Base):
    """Stores prompt optimization history for analytics."""

    __tablename__ = "prompt_optimizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True
    )

    # Source identification
    skill_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Prompt content
    original_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    optimized_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Scores
    original_score: Mapped[float] = mapped_column(Float, nullable=False)
    optimized_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Analysis and improvements
    improvements: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Metadata
    model_used: Mapped[str] = mapped_column(String(100), nullable=False, default="gpt-4o")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_optimizations_org_created", "org_id", "created_at"),
        Index("idx_optimizations_skill", "skill_name"),
    )

    # Relationships
    organization: Mapped["Organization | None"] = relationship(back_populates="optimizations")
