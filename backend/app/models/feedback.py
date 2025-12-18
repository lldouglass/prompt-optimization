"""User feedback model for evaluation and comparison results."""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class UserFeedback(Base):
    """Stores user feedback on evaluations and comparisons."""

    __tablename__ = "user_feedback"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Organization association
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True
    )

    # Optional link to a saved evaluation
    saved_evaluation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("saved_evaluations.id", ondelete="CASCADE"),
        nullable=True
    )

    # User who provided feedback
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    # Feedback type: "evaluation" or "comparison"
    feedback_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Core feedback fields
    agrees_with_result: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    quality_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Context snapshot - stores the evaluation/comparison data at time of feedback
    context_snapshot: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization | None"] = relationship()
    saved_evaluation: Mapped["SavedEvaluation | None"] = relationship()
    user: Mapped["User | None"] = relationship()
