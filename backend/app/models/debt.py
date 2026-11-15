from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func
from app.database import Base


class Debt(Base):
    __tablename__ = "debts"

    __table_args__ = (
        CheckConstraint(
            "total_amount > 0 AND monthly_payment > 0 "
            "AND remaining_amount >= 0 "
            "AND remaining_amount <= total_amount",
            name="check_debt_amount"
        ),
        CheckConstraint(
            "status IN ('active', 'paid', 'overdue')",
            name="check_debt_status"
        ),
        CheckConstraint(
            "interest_rate >= 0",
            name="check_interest_rate"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    debt_name = Column(String(150), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    interest_rate = Column(Numeric(5, 2), default=0)
    monthly_payment = Column(Numeric(15, 2), nullable=False)
    remaining_amount = Column(Numeric(15, 2), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())