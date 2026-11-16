
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date, datetime


class DebtPaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    payment_date: date
    notes: str | None = Field(default=None, max_length=255)


class DebtPaymentResponse(BaseModel):
    id: int
    debt_id: int
    user_id: int
    amount: Decimal
    payment_date: date
    notes: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DebtPaymentSummaryResponse(BaseModel):
    total_paid: Decimal
    payment_count: int
    last_payment_date: date | None = None

class DebtPaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    payment_date: date | None = None
    notes: str | None = Field(default=None, max_length=255)