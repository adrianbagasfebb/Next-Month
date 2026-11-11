from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

password_hash = PasswordHash.recommended()
# Mengamankan Password 
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# Memeriksa password 
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)

# Membuat Jwt
def create_access_token(user_id: int) -> str:

    if not JWT_SECRET_KEY:
raise RunTimeError("JWT_SECRET_KEY belum dikonfigurasi")

    expire = datetime.now(timezone.utc) + timedelta(

minutes=ACCESS_TOKEN_EXPIRE_MINUTES
)

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

    return token

