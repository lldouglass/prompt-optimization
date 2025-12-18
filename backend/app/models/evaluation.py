import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class SavedEvaluation(Base):
    """Stores saved evaluations and comparisons."""

    __tablename__ = "saved_evaluations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True
    )

    # Type: "evaluation" or "comparison"
    eval_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # The prompt/request
    request: Mapped[str] = mapped_column(Text, nullable=False)

    # For single evaluation
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # For comparison
    response_a: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_b: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_a: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model_b: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Results stored as JSON
    judgment: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    hallucination_check: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # For comparison results
    comparison_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    hallucination_check_a: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    hallucination_check_b: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization | None"] = relationship()
