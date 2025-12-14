import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Numeric, Index, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Request(Base):
    __tablename__ = "requests"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))

    # Request details
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    messages: Mapped[dict] = mapped_column(JSONB, nullable=False)
    parameters: Mapped[dict | None] = mapped_column(JSONB)

    # Response details
    response_content: Mapped[str | None] = mapped_column(Text)
    response_raw: Mapped[dict | None] = mapped_column(JSONB)

    # Metrics
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    cost_usd: Mapped[Decimal | None] = mapped_column(Numeric(10, 6))

    # Metadata
    prompt_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("prompts.id"))
    tags: Mapped[dict | None] = mapped_column(JSONB)
    trace_id: Mapped[str | None] = mapped_column(String(100))

    # Auto-evaluation fields
    evaluation_score: Mapped[float | None] = mapped_column(Float)
    evaluation_subscores: Mapped[dict | None] = mapped_column(JSONB)
    evaluation_tags: Mapped[list | None] = mapped_column(JSONB)
    evaluation_rationale: Mapped[str | None] = mapped_column(Text)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_requests_org_created", "org_id", "created_at"),
        Index("idx_requests_prompt", "prompt_id"),
        Index("idx_requests_trace", "trace_id"),
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="requests")
    prompt: Mapped["Prompt | None"] = relationship(back_populates="requests")
    test_results: Mapped[list["TestResult"]] = relationship(back_populates="request")
