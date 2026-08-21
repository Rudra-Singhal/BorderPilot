import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, ForeignKey, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ReliabilityScore(Base):
    """Deterministic score + tier, linked to a Counterparty and optionally to one
    Obligation. Append-only (versioned) — each recompute inserts a new row rather
    than overwriting, so score history for a counterparty/obligation is retained.
    """

    __tablename__ = "reliability_scores"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False
    )
    obligation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)
    tier: Mapped[str] = mapped_column(String(1), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    factors: Mapped[dict] = mapped_column(JSON, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
