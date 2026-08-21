import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Numeric, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class CurrencyExposure(Base):
    """Derived per-SME (or pool-wide when sme_id is null) net exposure by currency.
    Recomputed from open obligations; feeds the FX & Exposure screen."""

    __tablename__ = "currency_exposures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    gross_receivable_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    gross_payable_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    net_exposure_usd: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
