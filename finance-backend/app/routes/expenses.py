from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime
from typing import Optional
from loguru import logger

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.expense import Expense, Budget
from app.models.user import User
from app.schemas.expense import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse,
    ExpenseSummary, BudgetCreate, BudgetResponse
)
from app.ai.categorizer import categorize_expense

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ─── Expenses ────────────────────────────────────────────────────────────────

@router.post("/", response_model=ExpenseResponse, status_code=201)
async def create_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # AI categorization
    ai_result = await categorize_expense(payload.description, payload.amount)

    expense = Expense(
        user_id=current_user.id,
        amount=payload.amount,
        description=payload.description,
        notes=payload.notes,
        expense_date=payload.expense_date,
        category=ai_result["category"],
        category_confidence=ai_result["confidence"],
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    logger.info(f"Expense created: {expense.id} for user {current_user.id}")
    return expense


@router.get("/", response_model=list[ExpenseResponse])
def list_expenses(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

    if month:
        query = query.filter(extract("month", Expense.expense_date) == month)
    if year:
        query = query.filter(extract("year", Expense.expense_date) == year)
    if category:
        query = query.filter(Expense.category == category)

    total = query.count()
    expenses = (
        query.order_by(Expense.expense_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return expenses


@router.get("/summary", response_model=ExpenseSummary)
def get_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == current_user.id,
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year,
        )
        .all()
    )

    total = sum(e.amount for e in expenses)
    by_category: dict[str, float] = {}
    for e in expenses:
        cat = e.category or "Other"
        by_category[cat] = round(by_category.get(cat, 0) + e.amount, 2)

    return ExpenseSummary(
        total=round(total, 2),
        by_category=by_category,
        expense_count=len(expenses),
        month=month,
        year=year,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == current_user.id,
    ).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
    logger.info(f"Expense {expense_id} deleted by user {current_user.id}")


# ─── Budgets ─────────────────────────────────────────────────────────────────

@router.post("/budgets/", response_model=BudgetResponse, status_code=201)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Budget).filter(
        Budget.user_id == current_user.id,
        Budget.category == payload.category,
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Budget for this category already exists")

    budget = Budget(
        user_id=current_user.id,
        category=payload.category,
        monthly_limit=payload.monthly_limit,
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


@router.get("/budgets/", response_model=list[BudgetResponse])
def list_budgets(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    result = []

    for budget in budgets:
        spent = db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == current_user.id,
            Expense.category == budget.category,
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year,
        ).scalar() or 0.0

        result.append(BudgetResponse(
            id=budget.id,
            category=budget.category,
            monthly_limit=budget.monthly_limit,
            spent=round(spent, 2),
            remaining=round(budget.monthly_limit - spent, 2),
        ))

    return result
