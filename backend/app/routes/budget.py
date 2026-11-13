from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date

from app.database import get_db
from app.models.budget import Budget
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse
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
# 3. GET BUDGET BY ID
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
# 4. UPDATE BUDGET
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
# 5. DELETE BUDGET
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