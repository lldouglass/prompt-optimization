"""Agent session model for storing optimization agent state."""

import uuid
from datetime import datetime, timedelta
from typing import Literal
from sqlalchemy import String, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class AgentSession(Base):
    """Stores agent session state for pause/resume during optimization."""

    __tablename__ = "agent_sessions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True
    )

    # Session status
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="running"
    )  # running, awaiting_input, completed, failed

    agent_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="optimizer"
    )

    # Initial request data
    initial_request: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    # Agent state for resume
    conversation_history: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    tool_calls_made: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    pending_questions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    user_answers: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    questions_asked_count: Mapped[int] = mapped_column(nullable=False, default=0)

    # Intermediate results
    current_analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    current_score: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    web_sources: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # Final result
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow() + timedelta(hours=1)
    )

    __table_args__ = (
        Index("idx_agent_sessions_org_status", "org_id", "status"),
        Index("idx_agent_sessions_expires", "expires_at"),
    )

    # Relationships
    organization: Mapped["Organization | None"] = relationship()

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def can_ask_more_questions(self, max_questions: int = 3) -> bool:
        """Check if agent can ask more clarification questions."""
        return self.questions_asked_count < max_questions
