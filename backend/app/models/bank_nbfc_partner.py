import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PartnerType(str, enum.Enum):
    NBFC = "nbfc"
    BANK = "bank"


class BankNBFCPartner(Base):
    """A capital provider BorderPilot routes risk packets to. BorderPilot never lends;
    this entity models the separate institution that owns the final credit decision and
    disbursement. The mock NBFC service (Phase 5) acts on behalf of one of these rows."""

    __tablename__ = "bank_nbfc_partners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    partner_type: Mapped[PartnerType] = mapped_column(Enum(PartnerType), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    # lowest reliability tier this partner will finance without escalating to manual review
    min_auto_tier: Mapped[str] = mapped_column(String(1), nullable=False, default="B")
    typical_latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=1200)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
