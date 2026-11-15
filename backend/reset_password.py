from getpass import getpass

from app.database import SessionLocal
from app.models.user import User
from app.security import hash_password


db = SessionLocal()

try:
    email = "bagas@example.com"

    user = db.query(User).filter(User.email == email).first()

    if user is None:
        print("Akun tidak ditemukan.")
    else:
        password = getpass("Masukkan password baru: ")
        confirmation = getpass("Ulangi password baru: ")

        if len(password) < 8:
            print("Password minimal 8 karakter.")
        elif password != confirmation:
            print("Password tidak cocok.")
        else:
            user.password_hash = hash_password(password)
            db.commit()
            print("Password berhasil diperbarui!")

finally:
    db.close()