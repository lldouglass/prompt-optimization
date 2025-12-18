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
    usage_reset_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    requests: Mapped[list["Request"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    test_suites: Mapped[list["TestSuite"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    optimizations: Mapped[list["PromptOptimization"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
