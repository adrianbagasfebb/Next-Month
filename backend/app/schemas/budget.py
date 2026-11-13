from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import date, datetime

# ==========================================
# 1. BUDGET CREATE
# ==========================================

class BudgetCreate(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    amount: Decimal = Field(gt=0)
    budget_month: date


# ==========================================
# 2. BUDGET UPDATE
# ==========================================
class BudgetUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=1, max_length=100)
    amount: Decimal | None = Field(default=None, gt=0)
    budget_month: datetime | None = None

# ==========================================
# 3. BUDGET RESPONSE
# ==========================================
class BudgetResponse(BaseModel):
    id: int
    user_id: int
    category: str
    amount: Decimal
    budget_month: date
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)