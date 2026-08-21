import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer, ForeignKey, Enum, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class UnderwritingOutcome(str, enum.Enum):
    APPROVE = "approve"
    REVIEW = "review"
    REJECT = "reject"


class UnderwritingDecision(Base):
    """The lending decision layer on top of a raw ReliabilityScore: turns a score + tier
    into advance %, fee %, and an approve/review/reject outcome for one specific obligation.
    Versioned/append-only so a decision's basis is auditable."""

    __tablename__ = "underwriting_decisions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    obligation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False
    )
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False
    )
    reliability_score_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reliability_scores.id"), nullable=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    tier: Mapped[str] = mapped_column(String(1), nullable=False)
    advance_pct: Mapped[float] = mapped_column(Float, nullable=False)
    fee_pct: Mapped[float] = mapped_column(Float, nullable=False)
    outcome: Mapped[UnderwritingOutcome] = mapped_column(Enum(UnderwritingOutcome), nullable=False)
    limited_data: Mapped[bool] = mapped_column(nullable=False, default=False)
    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
