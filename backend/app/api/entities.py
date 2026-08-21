"""Read endpoints for the Phase 2 data-foundation entities. Seeded tables (invoices,
bank partners) get typed list endpoints; a counts endpoint exposes row counts across
every table so the data foundation can be verified end to end via the API."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.schemas import BankPartnerOut, InvoiceOut
from app.db.session import get_db
from app.models import (
    SME,
    AuditEvent,
    BankNBFCPartner,
    ComplianceRequirement,
    Counterparty,
    CurrencyExposure,
    FinancingAgreement,
    FinancingOffer,
    Invoice,
    LiquidityEvent,
    NettingRun,
    Obligation,
    OffsetMatch,
    PaymentBehaviorProfile,
    PaymentEvent,
    ReliabilityScore,
    Settlement,
    UnderwritingDecision,
)

router = APIRouter(tags=["entities"])

_COUNT_MODELS = {
    "smes": SME,
    "counterparties": Counterparty,
    "invoices": Invoice,
    "obligations": Obligation,
    "payment_events": PaymentEvent,
    "payment_behavior_profiles": PaymentBehaviorProfile,
    "reliability_scores": ReliabilityScore,
    "netting_runs": NettingRun,
    "offset_matches": OffsetMatch,
    "bank_nbfc_partners": BankNBFCPartner,
    "underwriting_decisions": UnderwritingDecision,
    "financing_offers": FinancingOffer,
    "financing_agreements": FinancingAgreement,
    "settlements": Settlement,
    "compliance_requirements": ComplianceRequirement,
    "liquidity_events": LiquidityEvent,
    "currency_exposures": CurrencyExposure,
    "audit_events": AuditEvent,
}


@router.get("/entities/counts")
def entity_counts(db: Session = Depends(get_db)):
    return {
        name: db.execute(select(func.count()).select_from(model)).scalar()
        for name, model in _COUNT_MODELS.items()
    }


@router.get("/invoices", response_model=list[InvoiceOut], tags=["invoices"])
def list_invoices(db: Session = Depends(get_db)):
    return db.execute(select(Invoice).order_by(Invoice.invoice_number)).scalars().all()


@router.get("/bank-partners", response_model=list[BankPartnerOut], tags=["bank-partners"])
def list_bank_partners(db: Session = Depends(get_db)):
    return db.execute(select(BankNBFCPartner).order_by(BankNBFCPartner.name)).scalars().all()
