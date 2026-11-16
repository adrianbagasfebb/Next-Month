
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from decimal import Decimal

from app.database import get_db
from app.models.debt import Debt
from app.models.debt_payment import DebtPayment
from app.models.user import User
from app.schemas.debt import (
    DebtCreate,
    DebtUpdate,
    DebtResponse,
    DebtSummaryResponse
)
from app.schemas.debt_payment import (
    DebtPaymentCreate,
    DebtPaymentResponse,
    DebtPaymentSummaryResponse
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
# 3. DEBT SUMMARY
# ==========================================

@router.get("/summary", response_model=DebtSummaryResponse)
def get_debt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    summary = db.query(
        func.coalesce(
            func.sum(Debt.total_amount), Decimal("0")
        ).label("total_debt"),

        func.coalesce(
            func.sum(Debt.remaining_amount), Decimal("0")
        ).label("remaining_debt"),

        func.coalesce(
            func.sum(Debt.monthly_payment), Decimal("0")
        ).label("total_monthly_payment"),

        func.count(
            case((Debt.status == "active", 1))
        ).label("active_debts"),

        func.count(
            case((Debt.status == "paid", 1))
        ).label("paid_debts"),

        func.count(
            case((Debt.status == "overdue", 1))
        ).label("overdue_debts")

    ).filter(
        Debt.user_id == current_user.id
    ).first()

    return {
        "total_debt": summary.total_debt,
        "remaining_debt": summary.remaining_debt,
        "total_monthly_payment": summary.total_monthly_payment,
        "active_debts": summary.active_debts,
        "paid_debts": summary.paid_debts,
        "overdue_debts": summary.overdue_debts
    }


# ==========================================
# 4. GET DEBT BY ID
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
# 5. UPDATE DEBT
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
# 6. DELETE DEBT
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


# ==========================================
# 7. CREATE DEBT PAYMENT
# ==========================================

@router.post(
    "/{debt_id}/payments",
    response_model=DebtPaymentResponse
)
def create_debt_payment(
    debt_id: int,
    payment_data: DebtPaymentCreate,
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

    if payment_data.amount > debt.remaining_amount:
        raise HTTPException(
            status_code=400,
            detail="Pembayaran melebihi sisa utang"
        )

    payment = DebtPayment(
        debt_id=debt.id,
        user_id=current_user.id,
        amount=payment_data.amount,
        payment_date=payment_data.payment_date,
        notes=payment_data.notes
    )

    debt.remaining_amount -= payment_data.amount

    if debt.remaining_amount == 0:
        debt.status = "paid"

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


# ==========================================
# 8. GET DEBT PAYMENT HISTORY
# ==========================================

@router.get(
    "/{debt_id}/payments",
    response_model=list[DebtPaymentResponse]
)
def get_debt_payments(
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

    payments = db.query(DebtPayment).filter(
        DebtPayment.debt_id == debt_id,
        DebtPayment.user_id == current_user.id
    ).order_by(
        DebtPayment.payment_date.desc(),
        DebtPayment.id.desc()
    ).all()

    return payments

# ==========================================
# 9. DEBT PAYMENT SUMMARY
# ==========================================

@router.get(
    "/{debt_id}/payments/summary",
    response_model=DebtPaymentSummaryResponse
)
def get_debt_payment_summary(
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

    summary = db.query(
        func.coalesce(
            func.sum(DebtPayment.amount),
            Decimal("0")
        ).label("total_paid"),

        func.count(
            DebtPayment.id
        ).label("payment_count"),

        func.max(
            DebtPayment.payment_date
        ).label("last_payment_date")

    ).filter(
        DebtPayment.debt_id == debt_id,
        DebtPayment.user_id == current_user.id
    ).first()

    return {
        "total_paid": summary.total_paid,
        "payment_count": summary.payment_count,
        "last_payment_date": summary.last_payment_date
    }
