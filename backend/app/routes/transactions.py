from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.transaction import Transaction
from app.models.userUser, 
from app.schemas.transaction import TransactionCreate, TransactionResponse

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)

# CREATE: Menambahkan transaksi baru
@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_transaction = Transaction(
        user_id=current_user.id,
        type=transaction.type,
        amount=transaction.amount,
        category=transaction.category,
        description=transaction.description,
        transaction_date=transaction.transaction_date,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

# READ: Mendapatkan semua transaksi untuk pengguna saat ini
@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = db.query(Transaction)\
        .filter(Transaction.user_id == current_user.id)\
        .all()
    
    return transactions

# READ: Menampilkan satu transaksi
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.query(Transaction)\
        .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)\
        .first()

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return transaction

# UPDATE: Memperbarui transaksi
@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.query(Transaction)\
    .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)\
        .first()

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    transaction.type = transaction_data.type
    transaction.amount = transaction_data.amount
    transaction.category = transaction_data.category
    transaction.description = transaction_data.description
    transaction.transaction_date = transaction_data.transaction_date

    db.commit()
    db.refresh(transaction)

    return transaction

# DELETE: Menghapus transaksi
@router.delete("/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.query(Transaction)\
    .filter(Transaction.id == transaction_id, Transaction.user_id == current_user.id)\
        .first()

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaksi berhasil dihapus",
        "transaction": transaction
    }
