import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class BankPacket(Base):
    """The M6 deliverable: a structured, exportable summary of one NettingRun --
    gross obligations in, proposed matches with tier/justification, net settlement
    figures, an FX/friction savings estimate, and flagged manual-review items.
    One packet per NettingRun; regenerating upserts in place (generated_at updates)."""

    __tablename__ = "bank_packets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    netting_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("netting_runs.id"), nullable=False, unique=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    gross_obligations_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    total_matched_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    net_settlement_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    fx_friction_savings_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    matches_count: Mapped[int] = mapped_column(Integer, nullable=False)
    auto_eligible_count: Mapped[int] = mapped_column(Integer, nullable=False)
    needs_review_count: Mapped[int] = mapped_column(Integer, nullable=False)
    body: Mapped[dict] = mapped_column(JSON, nullable=False)
