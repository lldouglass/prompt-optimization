import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DateTime, ForeignKey, Integer, Text, Boolean, Numeric, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class TestSuite(Base):
    __tablename__ = "test_suites"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"))
    prompt_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship(back_populates="test_suites")
    prompt: Mapped["Prompt"] = relationship(back_populates="test_suites")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="suite", cascade="all, delete-orphan")
    test_runs: Mapped[list["TestRun"]] = relationship(back_populates="suite", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    suite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_suites.id", ondelete="CASCADE"))
    name: Mapped[str | None] = mapped_column(String(255))
    variables: Mapped[dict] = mapped_column(JSONB, nullable=False)
    evaluators: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    suite: Mapped["TestSuite"] = relationship(back_populates="test_cases")
    test_results: Mapped[list["TestResult"]] = relationship(back_populates="test_case")


class TestRun(Base):
    __tablename__ = "test_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    suite_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_suites.id", ondelete="CASCADE"))
    prompt_version_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("prompt_versions.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    total_tests: Mapped[int | None] = mapped_column(Integer)
    passed_tests: Mapped[int | None] = mapped_column(Integer)
    failed_tests: Mapped[int | None] = mapped_column(Integer)
    avg_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    suite: Mapped["TestSuite"] = relationship(back_populates="test_runs")
    prompt_version: Mapped["PromptVersion"] = relationship(back_populates="test_runs")
    test_results: Mapped[list["TestResult"]] = relationship(back_populates="run", cascade="all, delete-orphan")


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_runs.id", ondelete="CASCADE"))
    test_case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("test_cases.id", ondelete="CASCADE"))
    request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("requests.id"))
    output: Mapped[str] = mapped_column(Text, nullable=False)
    evaluations: Mapped[dict] = mapped_column(JSONB, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_test_results_run", "run_id"),)

    # Relationships
    run: Mapped["TestRun"] = relationship(back_populates="test_results")
    test_case: Mapped["TestCase"] = relationship(back_populates="test_results")
    request: Mapped["Request | None"] = relationship(back_populates="test_results")
