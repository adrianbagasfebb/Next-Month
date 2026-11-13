from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.sql import func
from app.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    __table_args__ = (
        UniqueConstraint("user_id", "category", "budget_month"),
        CheckConstraint("amount > 0", name="check_budget_amount"),
    )

    id = Column(Integer, 
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    category = Column(
        String(100),
        nullable=False,
    )

    amount = Column(
        Numeric(15, 2),
        nullable=False,
    )

    budget_month = Column(
        Date,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
    )
