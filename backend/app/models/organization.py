import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Stripe subscription fields
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_plan: Mapped[str] = mapped_column(String(50), default="free")  # free, pro, team, enterprise
    subscription_status: Mapped[str] = mapped_column(String(50), default="active")  # active, past_due, canceled
    subscription_period_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Usage tracking
    requests_this_month: Mapped[int] = mapped_column(Integer, default=0)
    optimizations_this_month: Mapped[int] = mapped_column(Integer, default=0)
    tokens_used_this_month: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost_cents: Mapped[int] = mapped_column(Integer, default=0)  # Cost in cents (e.g., 23 = $0.23)
    usage_reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Referral program
    referral_code: Mapped[str | None] = mapped_column(String(12), unique=True, nullable=True, index=True)
    bonus_optimizations: Mapped[int] = mapped_column(Integer, default=0)  # Extra optimizations from referrals
    total_referrals: Mapped[int] = mapped_column(Integer, default=0)  # Count of successful referrals

    # Relationships
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    requests: Mapped[list["Request"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    test_suites: Mapped[list["TestSuite"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    optimizations: Mapped[list["PromptOptimization"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    members: Mapped[list["OrganizationMember"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
