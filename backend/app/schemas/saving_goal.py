
from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# CREATE SAVING GOAL
class SavingGoalCreate(BaseModel):
    goal_name: str = Field(min_length=1, max_length=150)
    target_amount: Decimal = Field(gt=0)
    target_date: date | None = None


# UPDATE SAVING GOAL
class SavingGoalUpdate(BaseModel):
    goal_name: str | None = Field(default=None, min_length=1, max_length=150)
    target_amount: Decimal | None = Field(default=None, gt=0)
    target_date: date | None = None
    status: Literal["active", "completed", "cancelled"] | None = None


# SAVING GOAL RESPONSE
class SavingGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    goal_name: str
    target_amount: Decimal
    current_amount: Decimal
    target_date: date | None
    status: str
    created_at: datetime


# CREATE SAVING TRANSACTION
class SavingTransactionCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    type: Literal["deposit", "withdrawal"]
    description: str | None = None
    transaction_date: date


# SAVING TRANSACTION RESPONSE
class SavingTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    saving_goal_id: int
    amount: Decimal
    type: str
    description: str | None
    transaction_date: date
    created_at: datetime
