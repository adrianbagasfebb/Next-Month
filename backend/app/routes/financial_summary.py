from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from decimal import Decimal
from datetime import date
from calendar import monthrange

from app.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.financial_summary import FinancialSummary, CategoryBreakdownResponse,  FinancialTrendsResponse
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/financial-summary",
    tags=["financial_summary"],
)


# ==========================================
# 1. FINANCIAL SUMMARY
# ==========================================

@router.get("/", response_model=FinancialSummary)
def get_financial_summary(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    selected_year = year or today.year
    selected_month = month or today.month

    start_date = date(selected_year, selected_month, 1)

    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1)
    else:
        end_date = date(selected_year, selected_month + 1, 1)

    result = db.query(
        func.coalesce(
            func.sum(
                case(
                    (Transaction.type == "income", Transaction.amount),
                    else_=0
                )
            ), 0
        ).label("total_income"),

        func.coalesce(
            func.sum(
                case(
                    (Transaction.type == "expense", Transaction.amount),
                    else_=0
                )
            ), 0
        ).label("total_expense")

    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date < end_date
    ).one()

    total_income = result.total_income
    total_expense = result.total_expense

    balance = total_income - total_expense

    return {
        "year": selected_year,
        "month": selected_month,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance
    }


# ==========================================
# 2. CATEGORY BREAKDOWN
# ==========================================

@router.get(
    "/category-breakdown",
    response_model=CategoryBreakdownResponse
)
def get_category_breakdown(
    year: int | None = Query(default=None, ge=2000, le=2100),
    month: int | None = Query(default=None, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    selected_year = year or today.year
    selected_month = month or today.month

    start_date = date(selected_year, selected_month, 1)

    if selected_month == 12:
        end_date = date(selected_year + 1, 1, 1)
    else:
        end_date = date(selected_year, selected_month + 1, 1)

    result = db.query(
        Transaction.category.label("category"),
        func.sum(Transaction.amount).label("total_amount")
    ).filter(
        Transaction.user_id == current_user.id,
        Transaction.type == "expense",
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date < end_date
    ).group_by(
        Transaction.category
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).all()

    total_expense = sum(
        (item.total_amount for item in result),
        Decimal("0.00")
    )

    categories = []

    for item in result:
        if total_expense > 0:
            percentage = (
                item.total_amount / total_expense * Decimal("100")
            ).quantize(Decimal("0.01"))
        else:
            percentage = Decimal("0.00")

        categories.append({
            "category": item.category,
            "total_amount": item.total_amount,
            "percentage": percentage
        })

    return {
        "year": selected_year,
        "month": selected_month,
        "total_expense": total_expense,
        "categories": categories
    }

# ==========================================
# 3. FINANCIAL TRENDS
# ==========================================
@router.get("/trends",response_model=FinancialTrendsResponse
)
def get_financial_trends(
    period_months: int = Query(default=6, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    today = date.today()

    # Menghitung awal periode
    current_month = today.month
    current_year = today.year

    start_month_index = (
        current_year * 12 + current_month - 1
        - (period_months - 1)
    )

    trends = []

    for i in range(period_months):
        month_index = start_month_index + i

        selected_year = month_index // 12
        selected_month = month_index % 12 + 1

        start_date = date(
            selected_year,
            selected_month,
            1
        )

        if selected_month == 12:
            end_date = date(selected_year + 1, 1, 1)
        else:
            end_date = date(
                selected_year,
                selected_month + 1,
                1
            )

        result = db.query(
            func.coalesce(
                func.sum(
                    case(
                        (Transaction.type == "income", Transaction.amount),
                        else_=0
                    )
                ), 0
            ).label("total_income"),

            func.coalesce(
                func.sum(
                    case(
                        (Transaction.type == "expense", Transaction.amount),
                        else_=0
                    )
                ), 0
            ).label("total_expense")

        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        ).one()

        total_income = result.total_income
        total_expense = result.total_expense

        balance = total_income - total_expense

        trends.append({
            "year": selected_year,
            "month": selected_month,
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": balance
        })

    return {
        "period_months": period_months,
        "trends": trends
    }