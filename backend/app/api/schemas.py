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
