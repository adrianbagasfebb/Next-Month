from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date, datetime

class DebtCreate(BaseModel):
    debt_name: str = Field(min_length=1, max_length=150)
    total_amount: Decimal = Field(gt=0)
    due_date: date | None = None

class DebtUpdate(BaseModel):
    debt_name: str | None = Field(default=None, min_length=1, max_length=150)
    total_amount: Decimal | None = Field(default=None, gt=0)
    interest_rate: Decimal | None = Field(default=None, ge=0, le=999.99)
    monthly_payment: Decimal | None = Field(default=None, gt=0)
    due_date: date | None = None

class DebtResponse(BaseModel):
    id: int
    user_id: int
    debt_name: str
    total_amount: Decimal
    interest_rate: Decimal
    monthly_payment: Decimal
    remaining_amount: Decimal
    due_date: date | None = None
    status: str
    created_at: datetime | None = None

model_config = ConfigDict(from_attributes=True)