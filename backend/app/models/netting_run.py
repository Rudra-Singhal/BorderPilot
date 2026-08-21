import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class NettingRun(Base):
    """A batch execution record: the set of obligations considered and how many
    matches came out of it. Non-destructive -- running netting never mutates
    Obligation rows, so a run is a repeatable proposal, not a settlement action."""

    __tablename__ = "netting_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    window_days: Mapped[int] = mapped_column(Integer, nullable=False)
    obligations_considered: Mapped[int] = mapped_column(Integer, nullable=False)
    matches_created: Mapped[int] = mapped_column(Integer, nullable=False)
    fx_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
