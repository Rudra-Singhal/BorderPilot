import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ComplianceStatus(str, enum.Enum):
    VERIFIED = "verified"
    PENDING = "pending"
    ILLUSTRATIVE = "illustrative"  # demo-only rule, NOT verified regulatory guidance


class ComplianceRequirement(Base):
    """A documentation/eligibility requirement attached to an obligation or financing
    agreement. The illustrative status is load-bearing: it is what keeps the compliance
    story honest -- anything not a well-established fact is flagged demo-illustrative."""

    __tablename__ = "compliance_requirements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    obligation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("obligations.id"), nullable=True
    )
    financing_agreement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("financing_agreements.id"), nullable=True
    )
    requirement_type: Mapped[str] = mapped_column(String(64), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ComplianceStatus] = mapped_column(Enum(ComplianceStatus), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
