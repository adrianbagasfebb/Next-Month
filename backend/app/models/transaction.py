from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    Text,
    ForeignKey
)
from sqlalchemy.sql import func

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    type = Column(String(10), nullable=False)

    amount = Column(Numeric(15, 2), nullable=False)

    category = Column(String(100), nullable=False)

    description = Column(Text, nullable=True)

    transaction_date = Column(Date, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )