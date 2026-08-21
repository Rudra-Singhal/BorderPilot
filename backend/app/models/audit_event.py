import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class AuditActor(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"


class AuditEvent(Base):
    """Append-only audit trail: every score computed, offer generated, lender request,
    netting match, and settlement. Doubles as the compliance/trust story and the
    Activity screen's data source."""

    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor: Mapped[AuditActor] = mapped_column(Enum(AuditActor), nullable=False, default=AuditActor.SYSTEM)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
