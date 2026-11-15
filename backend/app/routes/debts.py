from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from decimal import Decimal
from datetime import date

from app.database import get_db
from app.models.debt import Debt
from app.models.user import User
from app.schemas.debt import (
    DebtCreate,
    DebtUpdate,
    DebtResponse
)
from app.dependencies import get_current_user


router = APIRouter(
    prefix="/debts",
    tags=["Debt Management"]
)


# ==========================================
# 1. CREATE DEBT
# ==========================================

@router.post("/", response_model=DebtResponse)
def create_debt(
    debt_data: DebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_debt = Debt(
        user_id=current_user.id,
        debt_name=debt_data.debt_name,
        total_amount=debt_data.total_amount,
        interest_rate=debt_data.interest_rate,
        monthly_payment=debt_data.monthly_payment,
        remaining_amount=debt_data.total_amount,
        due_date=debt_data.due_date,
        status="active"
    )

    db.add(new_debt)
    db.commit()
    db.refresh(new_debt)

    return new_debt


# ==========================================
# 2. GET ALL DEBTS
# ==========================================

@router.get("/", response_model=list[DebtResponse])
def get_debts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    debts = db.query(Debt).filter(
        Debt.user_id == current_user.id
    ).order_by(Debt.created_at.desc()).all()

    return debts


# ==========================================
# 3. GET DEBT BY ID
# ==========================================

@router.get("/{debt_id}", response_model=DebtResponse)
def get_debt(
    debt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()

    if debt is None:
        raise HTTPException(
            status_code=404,
            detail="Utang tidak ditemukan"
        )

    return debt


# ==========================================
# 4. UPDATE DEBT
# ==========================================

@router.put("/{debt_id}", response_model=DebtResponse)
def update_debt(
    debt_id: int,
    debt_data: DebtUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()

    if debt is None:
        raise HTTPException(
            status_code=404,
            detail="Utang tidak ditemukan"
        )

    update_data = debt_data.model_dump(exclude_unset=True)

    if "total_amount" in update_data:
        new_total = update_data["total_amount"]

        paid_amount = debt.total_amount - debt.remaining_amount
        new_remaining = new_total - paid_amount

        if new_remaining < 0:
            raise HTTPException(
                status_code=400,
                detail="Total utang baru tidak boleh lebih kecil dari jumlah yang sudah dibayar"
            )

        debt.total_amount = new_total
        debt.remaining_amount = new_remaining

        if new_remaining == 0:
            debt.status = "paid"
        else:
            debt.status = "active"

        update_data.pop("total_amount")

    for field, value in update_data.items():
        setattr(debt, field, value)

    db.commit()
    db.refresh(debt)

    return debt


# ==========================================
# 5. DELETE DEBT
# ==========================================

@router.delete("/{debt_id}")
def delete_debt(
    debt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    debt = db.query(Debt).filter(
        Debt.id == debt_id,
        Debt.user_id == current_user.id
    ).first()

    if debt is None:
        raise HTTPException(
            status_code=404,
            detail="Utang tidak ditemukan"
        )

    db.delete(debt)
    db.commit()

    return {
        "message": "Data utang berhasil dihapus"
    }