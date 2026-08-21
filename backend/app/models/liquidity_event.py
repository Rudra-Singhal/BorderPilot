import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Numeric, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class LiquidityEvent(Base):
    """Logged every time an Unlock Liquidity action fires -- links the receivable and the
    offer to the cash-runway impact, so the 'we closed the gap' moment is a real record."""

    __tablename__ = "liquidity_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    obligation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=True
    )
    financing_offer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financing_offers.id"), nullable=True
    )
    cash_before_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    cash_after_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    runway_delta_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
