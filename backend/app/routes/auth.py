from fastapi import APIRouter, Depends, HTTPException
from sqlachemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.security import hash_password, verify_password
from app.dependencies import get_current_user

router = APIRouter(
    prefix="/auth", 
    tags=["Authentication"]
)

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # Periksa apakah email sudah terdaftar
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=409, detail="Email sudah terdaftar")

    # 2 Hash password sebelum disimpan
    hashed_password = hash_password(user.password)

    # 3 buat objek pengguna baru
    new_user = User(
        full_name=user.full_name,
        email=user.email,
        hashed_password=hashed_password
    )

    # 4 simpan pengguna baru ke database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 5 kembalikan data pengguna baru
    return new_user

# Login
@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):

# Cari Pengguna Berdasarkan Email
existing_user = db.query(User).filter(
    User.email == User.email
).first()

# Periksa email dan password 
if not existing_user or not verify_password(
    user.password,
    existing_user.password_hash
    ):
raise HTTPException(
    status_code=401,
    detail="Email atau password salah"
    )

# 3. Buat JWT
access_token= create_access_token(existing_user.id)

# 4. Kembalikan token
return {
   "access_token": access_token,
   "token_type": "bearer"
   }

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user