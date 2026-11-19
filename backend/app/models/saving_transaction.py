
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class SavingTransaction(Base):
    __tablename__ = "saving_transactions"

    id = Column(Integer, primary_key=True, index=True)

    saving_goal_id = Column(
        Integer,
        ForeignKey("saving_goals.id", ondelete="CASCADE"),
        nullable=False
    )

    amount = Column(
        Numeric(15, 2),
        nullable=False
    )

    type = Column(
        String(10),
        nullable=False
    )

    description = Column(Text, nullable=True)

    transaction_date = Column(
        Date,
        nullable=False
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    saving_goal = relationship(
        "SavingGoal",
        back_populates="transactions"
    )
