from pydantic import BaseModel
from decimal import Decimal

class FinancialSummary(BaseModel):
    year: int
    month: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal

class CategoryBreakdownItem(BaseModel):
    category: str
    total_amount: Decimal
    percentage: Decimal

class CategoryBreakdownResponse(BaseModel):
    year: int
    month: int
    total_expense: Decimal
    categories: list[CategoryBreakdownItem]

class MonthlyTrendItem(BaseModel):
    year: int
    month: int
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal

class FinancialTrendResponse(BaseModel):
    trend: list[MonthlyTrendItem]

