import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Referral(Base):
    """Tracks referral relationships between organizations."""
    __tablename__ = "referrals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # The organization that made the referral
    referrer_org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # The user who signed up via referral
    referred_user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # The organization created by the referred user
    referred_org_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    # Reward amounts (in optimizations)
    referrer_reward: Mapped[int] = mapped_column(Integer, default=50)
    referee_reward: Mapped[int] = mapped_column(Integer, default=25)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    referrer_org: Mapped["Organization"] = relationship(
        "Organization", foreign_keys=[referrer_org_id]
    )
    referred_user: Mapped["User"] = relationship("User")
    referred_org: Mapped["Organization"] = relationship(
        "Organization", foreign_keys=[referred_org_id]
    )
