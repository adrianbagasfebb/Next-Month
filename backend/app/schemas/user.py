from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime


# Schema untuk menerima data registrasi
class UserCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)


# Schema untuk menampilkan data pengguna
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)