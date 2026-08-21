import enum
import uuid
from datetime import date, datetime

from sqlalchemy import String, DateTime, Date, Numeric, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.obligation import ObligationDirection


class InvoiceSource(str, enum.Enum):
    SEEDED = "seeded"
    EXTRACTED = "extracted"  # pulled from an uploaded document via the extraction layer


class Invoice(Base):
    """The trade document a Receivable/Payable derives from. One Invoice -> one Obligation
    in the demo; kept as its own entity so the document-extraction and compliance stories
    have a real record to attach to."""

    __tablename__ = "invoices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sme_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("smes.id"), nullable=False)
    counterparty_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("counterparties.id"), nullable=False
    )
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False)
    direction: Mapped[ObligationDirection] = mapped_column(Enum(ObligationDirection), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(14, 2, asdecimal=False), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    po_reference: Mapped[str | None] = mapped_column(String(64), nullable=True)
    source: Mapped[InvoiceSource] = mapped_column(
        Enum(InvoiceSource), nullable=False, default=InvoiceSource.SEEDED
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
