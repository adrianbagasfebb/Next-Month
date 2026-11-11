from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from decimal import Decimal
from typing import Literal


class TransactionCreate(BaseModel):
    type: Literal["income", "expense"]
    amount: Decimal = Field(
        gt=0,
        max_digits=15,
        decimal_places=2
    )
    category: str = Field(min_length=2, max_length=100)
    description: str | None = None
    transaction_date: date


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    type: str
    amount: Decimal
    category: str
    description: str | None
    transaction_date: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)