import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class FinancingStage(str, enum.Enum):
    OPPORTUNITY = "opportunity"
    OFFER = "offer"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    DISBURSED = "disbursed"
    SETTLED = "settled"


class LenderDecision(str, enum.Enum):
    APPROVE = "approve"
    REVIEW = "review"
    REJECT = "reject"


class FinancingAgreement(Base):
    """Tracks one accepted offer through the financing pipeline. The stage machine advances
    as the (separate) mock NBFC service responds and as settlement fast-forward fires.
    A receivable can have at most one active agreement -- the double-financing guard."""

    __tablename__ = "financing_agreements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    financing_offer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financing_offers.id"), nullable=False
    )
    obligation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=False
    )
    bank_nbfc_partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bank_nbfc_partners.id"), nullable=True
    )
    stage: Mapped[FinancingStage] = mapped_column(
        Enum(FinancingStage), nullable=False, default=FinancingStage.OFFER
    )
    lender_decision: Mapped[LenderDecision | None] = mapped_column(Enum(LenderDecision), nullable=True)
    disbursed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
