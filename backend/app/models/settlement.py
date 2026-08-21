import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Numeric, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class SettlementType(str, enum.Enum):
    NET = "net"  # residual after a netting offset
    DIRECT = "direct"  # a gross obligation settled directly
    FINANCING = "financing"  # buyer payment arriving to close out a financed receivable


class Settlement(Base):
    """A record of money actually moving (or being marked settled in the demo's
    fast-forward). Linked to whichever mechanism produced it -- a netting residual, a
    direct settlement, or a financed receivable maturing."""

    __tablename__ = "settlements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    settlement_type: Mapped[SettlementType] = mapped_column(Enum(SettlementType), nullable=False)
    offset_match_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("offset_matches.id"), nullable=True
    )
    financing_agreement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financing_agreements.id"), nullable=True
    )
    obligation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=True
    )
    amount_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    settled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
