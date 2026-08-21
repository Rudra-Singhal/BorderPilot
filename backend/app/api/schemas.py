import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.models.obligation import ObligationDirection, ObligationStatus


class SMEOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    country: str
    base_currency: str
    created_at: datetime


class CounterpartyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    country: str
    created_at: datetime


class ObligationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    sme_id: uuid.UUID
    counterparty_id: uuid.UUID
    direction: ObligationDirection
    amount: float
    currency: str
    expected_settlement_date: date
    status: ObligationStatus
    created_at: datetime


class PaymentEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    counterparty_id: uuid.UUID
    sme_id: uuid.UUID
    obligation_id: uuid.UUID | None
    due_date: date
    paid_date: date
    amount: float
    currency: str
    created_at: datetime


class PaymentBehaviorProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    counterparty_id: uuid.UUID
    on_time_ratio: float
    median_delay_days: float
    delay_variance: float
    transaction_count: int
    most_recent_payment_date: date
    computed_at: datetime


class ReliabilityScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    counterparty_id: uuid.UUID
    obligation_id: uuid.UUID | None
    score: float
    tier: str
    version: int
    factors: dict
    computed_at: datetime


class OffsetMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    netting_run_id: uuid.UUID
    counterparty_id: uuid.UUID
    payable_obligation_id: uuid.UUID
    receivable_obligation_id: uuid.UUID
    settlement_bucket_start: date
    settlement_bucket_end: date
    matched_amount_usd: float
    created_at: datetime


class NettingRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    executed_at: datetime
    window_days: int
    obligations_considered: int
    matches_created: int
    fx_snapshot: dict


class NettingRunDetailOut(NettingRunOut):
    matches: list[OffsetMatchOut]


class ResidualOut(BaseModel):
    obligation_id: uuid.UUID
    sme_id: uuid.UUID
    counterparty_id: uuid.UUID
    direction: str
    total_usd: float
    matched_usd: float
    residual_usd: float
    fully_matched: bool
