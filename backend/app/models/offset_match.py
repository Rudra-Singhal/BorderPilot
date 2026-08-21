import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, Date, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OffsetMatch(Base):
    """One netted pair: a payable obligation (an SME owes the counterparty) offset
    against a receivable obligation (the counterparty owes an SME), routed through
    their shared pooled Counterparty. Multilateral netting falls out of multiple
    OffsetMatch rows sharing the same counterparty + settlement bucket."""

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
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
