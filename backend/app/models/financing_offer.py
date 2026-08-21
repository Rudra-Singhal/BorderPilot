import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, DateTime, Date, Numeric, Float, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class OfferStatus(str, enum.Enum):
    PRESENTED = "presented"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class FinancingOffer(Base):
    """A concrete advance offer against one obligation, priced off its UnderwritingDecision
    and routed to a specific BankNBFCPartner. BorderPilot generates this; the partner funds it."""

    __tablename__ = "financing_offers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    obligation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False
    )
    underwriting_decision_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("underwriting_decisions.id"), nullable=True
    )
    bank_nbfc_partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bank_nbfc_partners.id"), nullable=True
    )
    invoice_amount: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    advance_pct: Mapped[float] = mapped_column(Float, nullable=False)
    fee_pct: Mapped[float] = mapped_column(Float, nullable=False)
    advance_amount_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    fee_amount_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    net_proceeds_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    maturity_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[OfferStatus] = mapped_column(Enum(OfferStatus), nullable=False, default=OfferStatus.PRESENTED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
