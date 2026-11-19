
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class SavingGoal(Base):
    __tablename__ = "saving_goals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    goal_name = Column(String(150), nullable=False)
    target_amount = Column(Numeric(15, 2), nullable=False)

    current_amount = Column(
        Numeric(15, 2),
        nullable=False,
        default=0,
        server_default="0"
    )

    target_date = Column(Date, nullable=True)

    status = Column(
        String(20),
        nullable=False,
        default="active",
        server_default="active"
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="saving_goals"
    )

    transactions = relationship(
        "SavingTransaction",
        back_populates="saving_goal",
        cascade="all, delete-orphan"
    )
