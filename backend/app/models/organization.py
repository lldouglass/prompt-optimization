import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    api_keys: Mapped[list["ApiKey"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    requests: Mapped[list["Request"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    test_suites: Mapped[list["TestSuite"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    optimizations: Mapped[list["PromptOptimization"]] = relationship(back_populates="organization", cascade="all, delete-orphan")
