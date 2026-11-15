from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import date
from decimal import Decimal

from app.database import get_db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetSummaryItem,
    BudgetSummaryResponse
)
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/budgets",
    tags=["Budgets"]
)


# ==========================================
# 1. CREATE BUDGET
# ==========================================

@router.post(
    "/",
    response_model=BudgetResponse,
    status_code=status.HTTP_201_CREATED
)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget_month = date(
        budget_data.budget_month.year,
        budget_data.budget_month.month,
        1
    )

    new_budget = Budget(
        user_id=current_user.id,
        category=budget_data.category,
        amount=budget_data.amount,
        budget_month=budget_month
    )

    db.add(new_budget)

    try:
        db.commit()
        db.refresh(new_budget)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Anggaran untuk kategori dan bulan tersebut sudah ada"
        )

    return new_budget


# ==========================================
# 2. GET ALL BUDGETS
# ==========================================

@router.get(
    "/",
    response_model=list[BudgetResponse]
)
def get_budgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id
    ).order_by(
        Budget.budget_month.desc()
    ).all()

    return budgets

# ==========================================
# 3. BUDGET SUMMARY
# ==========================================

@router.get(
    "/summary",
    response_model=BudgetSummaryResponse
)
def get_budget_summary(
    budget_month: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if budget_month is None:
        budget_month = date.today()

    start_date = date(
        budget_month.year,
        budget_month.month,
        1
    )

    if start_date.month == 12:
        end_date = date(start_date.year + 1, 1, 1)
    else:
        end_date = date(
            start_date.year,
            start_date.month + 1,
            1
        )

    budgets = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.budget_month == start_date
    ).all()

    categories = []

    total_budget = Decimal("0")
    total_spent = Decimal("0")

    for budget in budgets:

        spent = db.query(
            func.coalesce(func.sum(Transaction.amount), 0)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.type == "expense",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date < end_date
        ).scalar()

        spent = Decimal(str(spent))
        budget_amount = Decimal(str(budget.amount))

        remaining = budget_amount - spent
        usage = (spent / budget_amount) * 100

        if usage >= 100:
            status_budget = "Melebihi anggaran"
        elif usage >= 80:
            status_budget = "Hampir habis"
        else:
            status_budget = "Aman"

        categories.append(
            BudgetSummaryItem(
                category=budget.category,
                budget_amount=budget_amount,
                spent_amount=spent,
                remaining_amount=remaining,
                usage_percentage=round(usage, 2),
                status=status_budget
            )
        )

        total_budget += budget_amount
        total_spent += spent

    return BudgetSummaryResponse(
        budget_month=start_date,
        total_budget=total_budget,
        total_spent=total_spent,
        total_remaining=total_budget - total_spent,
        categories=categories
    )

# ==========================================
# 4. GET BUDGET BY ID
# ==========================================

@router.get(
    "/{budget_id}",
    response_model=BudgetResponse
)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Anggaran tidak ditemukan"
        )

    return budget


# ==========================================
# 5. UPDATE BUDGET
# ==========================================

@router.put(
    "/{budget_id}",
    response_model=BudgetResponse
)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Anggaran tidak ditemukan"
        )

    update_data = budget_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Tidak ada data yang diubah"
        )

    if "budget_month" in update_data:
        selected_date = update_data["budget_month"]

        update_data["budget_month"] = date(
            selected_date.year,
            selected_date.month,
            1
        )

    for key, value in update_data.items():
        setattr(budget, key, value)

    try:
        db.commit()
        db.refresh(budget)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Anggaran untuk kategori dan bulan tersebut sudah ada"
        )

    return budget


# ==========================================
# 6. DELETE BUDGET
# ==========================================

@router.delete(
    "/{budget_id}"
)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == current_user.id
    ).first()

    if budget is None:
        raise HTTPException(
            status_code=404,
            detail="Anggaran tidak ditemukan"
        )

    db.delete(budget)
    db.commit()

    return {
        "message": "Anggaran berhasil dihapus"
    }