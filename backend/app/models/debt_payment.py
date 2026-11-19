
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    Date,
    DateTime,
    String,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class DebtPayment(Base):
    __tablename__ = "debt_payments"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="check_payment_amount"
        ),
    )

    id = Column(Integer, primary_key=True, index=True)

    debt_id = Column(
        Integer,
        ForeignKey("debts.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    amount = Column(Numeric(15, 2), nullable=False)

    payment_date = Column(Date, nullable=False)

    notes = Column(String(255), nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    debt = relationship("Debt",      back_populates="payments")
    user = relationship("User")