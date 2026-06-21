from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Index, func, Text
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=True)          # AI-assigned
    category_confidence = Column(Float, nullable=True)    # AI confidence score
    notes = Column(Text, nullable=True)
    expense_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="expenses")

    # ── Indexes for fast filtering ──────────────────────────────────────────
    __table_args__ = (
        Index("ix_expenses_user_date", "user_id", "expense_date"),       # monthly queries
        Index("ix_expenses_user_category", "user_id", "category"),       # category breakdown
    )


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(50), nullable=False)
    monthly_limit = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="budgets")

    __table_args__ = (
        Index("ix_budgets_user_category", "user_id", "category"),
    )
