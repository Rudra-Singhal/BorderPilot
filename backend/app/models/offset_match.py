import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, DateTime, Date, Numeric, String, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OffsetMatch(Base):
    """One netted pair: a payable obligation (an SME owes the counterparty) offset
    against a receivable obligation (the counterparty owes an SME), routed through
    their shared pooled Counterparty. Multilateral netting falls out of multiple
    OffsetMatch rows sharing the same counterparty + settlement bucket.

    confidence_tier/eligibility_flag/justification_text/ai_generated are populated by
    M5's explanation layer at creation time; nullable because Phase 4 rows predate it.
    """

    __tablename__ = "offset_matches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    netting_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("netting_runs.id"), nullable=False
    )
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False
    )
    payable_obligation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False
    )
    receivable_obligation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False
    )
    settlement_bucket_start: Mapped[date] = mapped_column(Date, nullable=False)
    settlement_bucket_end: Mapped[date] = mapped_column(Date, nullable=False)
    matched_amount_usd: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    confidence_tier: Mapped[str | None] = mapped_column(String(1), nullable=True)
    eligibility_flag: Mapped[str | None] = mapped_column(String(20), nullable=True)
    justification_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_generated: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
