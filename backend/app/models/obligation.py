import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, DateTime, Date, Numeric, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ObligationDirection(str, enum.Enum):
    RECEIVABLE = "receivable"  # money owed TO the SME
    PAYABLE = "payable"  # money owed BY the SME


class ObligationStatus(str, enum.Enum):
    OPEN = "open"
    SETTLED = "settled"
    NETTED = "netted"


class Obligation(Base):
    """Generalizes Receivable/Payable — an edge in the netting graph."""

    __tablename__ = "obligations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False
    )
    direction: Mapped[ObligationDirection] = mapped_column(Enum(ObligationDirection), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    expected_settlement_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[ObligationStatus] = mapped_column(
        Enum(ObligationStatus), nullable=False, default=ObligationStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
