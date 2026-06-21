from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional


VALID_CATEGORIES = [
    "Food & Dining",
    "Transport",
    "Shopping",
    "Bills & Utilities",
    "Health",
    "Entertainment",
    "Education",
    "Travel",
    "Personal Care",
    "Other",
]


class ExpenseCreate(BaseModel):
    amount: float
    description: str
    notes: Optional[str] = None
    expense_date: datetime

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return round(v, 2)

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Description cannot be empty")
        return v.strip()


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    expense_date: Optional[datetime] = None
    category: Optional[str] = None


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    description: str
    category: Optional[str]
    category_confidence: Optional[float]
    notes: Optional[str]
    expense_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseSummary(BaseModel):
    total: float
    by_category: dict[str, float]
    expense_count: int
    month: int
    year: int


class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float

    @field_validator("category")
    @classmethod
    def valid_category(cls, v):
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {VALID_CATEGORIES}")
        return v

    @field_validator("monthly_limit")
    @classmethod
    def limit_positive(cls, v):
        if v <= 0:
            raise ValueError("Budget limit must be greater than 0")
        return v


class BudgetResponse(BaseModel):
    id: int
    category: str
    monthly_limit: float
    spent: Optional[float] = 0.0
    remaining: Optional[float] = None

    class Config:
        from_attributes = True
