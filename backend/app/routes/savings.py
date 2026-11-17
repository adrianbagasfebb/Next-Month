
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.saving_goal import SavingGoal
from app.models.saving_transaction import SavingTransaction

from app.schemas.saving_goal import (
    SavingGoalCreate,
    SavingGoalUpdate,
    SavingGoalResponse,
    SavingTransactionCreate,
    SavingTransactionResponse,
)

from decimal import Decimal


router = APIRouter(
    prefix="/savings",
    tags=["Saving Goals"]
)


# ==========================================
# 1. CREATE SAVING GOAL
# ==========================================

@router.post("/", response_model=SavingGoalResponse)
def create_saving_goal(
    goal_data: SavingGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_goal = SavingGoal(
        user_id=current_user.id,
        goal_name=goal_data.goal_name,
        target_amount=goal_data.target_amount,
        current_amount=Decimal("0"),
        target_date=goal_data.target_date,
        status="active"
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal


# ==========================================
# 2. GET ALL SAVING GOALS
# ==========================================

@router.get("/", response_model=list[SavingGoalResponse])
def get_saving_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goals = db.query(SavingGoal).filter(
        SavingGoal.user_id == current_user.id
    ).order_by(SavingGoal.created_at.desc()).all()

    return goals


# ==========================================
# 3. GET SAVING GOAL BY ID
# ==========================================

@router.get("/{goal_id}", response_model=SavingGoalResponse)
def get_saving_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Target tabungan tidak ditemukan"
        )

    return goal


# ==========================================
# 4. UPDATE SAVING GOAL
# ==========================================

@router.put("/{goal_id}", response_model=SavingGoalResponse)
def update_saving_goal(
    goal_id: int,
    goal_data: SavingGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Target tabungan tidak ditemukan"
        )

    update_data = goal_data.model_dump(exclude_unset=True)

    new_target = update_data.get("target_amount", goal.target_amount)

    if new_target is not None and new_target < goal.current_amount:
        raise HTTPException(
            status_code=400,
            detail="Target tabungan tidak boleh lebih kecil dari saldo saat ini"
        )

    for field, value in update_data.items():
        if value is not None or field == "target_date":
            setattr(goal, field, value)

    if goal.current_amount >= goal.target_amount:
        goal.status = "completed"
    elif goal.status == "completed":
        goal.status = "active"

    db.commit()
    db.refresh(goal)

    return goal


# ==========================================
# 5. CREATE SAVING TRANSACTION
# ==========================================

@router.post(
    "/{goal_id}/transactions",
    response_model=SavingTransactionResponse
)
def create_saving_transaction(
    goal_id: int,
    transaction_data: SavingTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Target tabungan tidak ditemukan"
        )

    amount = transaction_data.amount

    if goal.status != "active":
        raise HTTPException(
            status_code=400,
            detail="Target tabungan tidak dalam status aktif"
        )

    if transaction_data.type == "deposit":
        if goal.current_amount + amount > goal.target_amount:
            raise HTTPException(
                status_code=400,
                detail="Setoran melebihi target tabungan"
            )

        goal.current_amount += amount

    elif transaction_data.type == "withdrawal":
        if amount > goal.current_amount:
            raise HTTPException(
                status_code=400,
                detail="Penarikan melebihi saldo tabungan"
            )

        goal.current_amount -= amount

    if goal.current_amount == goal.target_amount:
        goal.status = "completed"
    else:
        goal.status = "active"

    new_transaction = SavingTransaction(
        saving_goal_id=goal.id,
        amount=amount,
        type=transaction_data.type,
        description=transaction_data.description,
        transaction_date=transaction_data.transaction_date
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


# ==========================================
# 6. GET SAVING TRANSACTION HISTORY
# ==========================================

@router.get(
    "/{goal_id}/transactions",
    response_model=list[SavingTransactionResponse]
)
def get_saving_transactions(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Target tabungan tidak ditemukan"
        )

    transactions = db.query(SavingTransaction).filter(
        SavingTransaction.saving_goal_id == goal_id
    ).order_by(
        SavingTransaction.transaction_date.desc(),
        SavingTransaction.id.desc()
    ).all()

    return transactions


# ==========================================
# 7. DELETE SAVING GOAL
# ==========================================

@router.delete("/{goal_id}")
def delete_saving_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    goal = db.query(SavingGoal).filter(
        SavingGoal.id == goal_id,
        SavingGoal.user_id == current_user.id
    ).first()

    if goal is None:
        raise HTTPException(
            status_code=404,
            detail="Target tabungan tidak ditemukan"
        )

    db.delete(goal)
    db.commit()

    return {
        "message": "Target tabungan berhasil dihapus"
    }
