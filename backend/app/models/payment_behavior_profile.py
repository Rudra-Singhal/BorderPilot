import uuid
from datetime import date, datetime

from sqlalchemy import DateTime, Date, Float, Integer, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PaymentBehaviorProfile(Base):
    """Derived, pooled behavior profile per Counterparty, aggregated across all SMEs' PaymentEvents."""

    __tablename__ = "payment_behavior_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False, unique=True
    )
    on_time_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    median_delay_days: Mapped[float] = mapped_column(Float, nullable=False)
    delay_variance: Mapped[float] = mapped_column(Float, nullable=False)
    transaction_count: Mapped[int] = mapped_column(Integer, nullable=False)
    most_recent_payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
