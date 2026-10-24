
import math

import psycopg
from fastapi import FastAPI, Query, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field

from database import get_db
from users import router as users_router, get_current_user

app = FastAPI()
app.include_router(users_router)


class Expense(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    amount: float = Field(gt=0)
    category: str = "Other"


@app.get("/")
def health():
    return {"message": "Expense Tracker API is running"}


@app.get("/expenses")
def get_expenses(
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        "SELECT * FROM expenses WHERE user_id = %s",
        (current_user["id"],)
    )
    return {"expenses": cursor.fetchall()}


@app.post("/expenses", status_code=status.HTTP_201_CREATED)
def create_expense(
    expense: Expense,
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        INSERT INTO expenses (title, amount, category, user_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (
            expense.title,
            expense.amount,
            expense.category,
            current_user["id"]
        )
    )

    expense_id = cursor.fetchone()["id"]
    connection.commit()

    return {
        "message": "Expense created successfully",
        "id": expense_id,
        "title": expense.title,
        "amount": expense.amount,
        "category": expense.category
    }


@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int = Path(gt=0),
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        "DELETE FROM expenses WHERE id = %s AND user_id = %s",
        (expense_id, current_user["id"])
    )

    connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {"message": "Expense deleted successfully"}


@app.get("/expenses/filter")
def filter_expenses(
    min_amount: float = Query(ge=0),
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        SELECT * FROM expenses
        WHERE amount > %s AND user_id = %s
        """,
        (min_amount, current_user["id"])
    )
    return {"expenses": cursor.fetchall()}


@app.get("/expenses/summary")
def expense_summary(
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        SELECT COUNT(*) AS total_expenses,
               COALESCE(SUM(amount), 0) AS total_amount
        FROM expenses
        WHERE user_id = %s
        """,
        (current_user["id"],)
    )

    summary = cursor.fetchone()

    return {
        "total_expenses": summary["total_expenses"],
        "total_amount": summary["total_amount"]
    }


@app.get("/expenses/category")
def filter_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        SELECT * FROM expenses
        WHERE category = %s AND user_id = %s
        """,
        (category, current_user["id"])
    )

    expenses = cursor.fetchall()

    if not expenses:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return {"expenses": expenses}


@app.put("/update/expenses/{expense_id}/{amount}")
def update_expense(
    expense_id: int = Path(gt=0),
    amount: float = Path(gt=0),
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        UPDATE expenses
        SET amount = %s
        WHERE id = %s AND user_id = %s
        """,
        (amount, expense_id, current_user["id"])
    )

    connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {"message": "Expense updated successfully"}


@app.patch("/expenses/{expense_id}")
def update_expense_category(
    expense_id: int = Path(gt=0),
    category: str = Query(min_length=1),
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        UPDATE expenses
        SET category = %s
        WHERE id = %s AND user_id = %s
        """,
        (category, expense_id, current_user["id"])
    )

    connection.commit()

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {"message": "Expense updated successfully"}


@app.get("/expenses/total-by-category")
def total_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total_amount
        FROM expenses
        WHERE category = %s AND user_id = %s
        """,
        (category, current_user["id"])
    )

    result = cursor.fetchone()
    return {"total_amount": result["total_amount"]}


@app.get("/expenses/count-by-category")
def count_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        SELECT COUNT(*) AS count_category
        FROM expenses
        WHERE category = %s AND user_id = %s
        """,
        (category, current_user["id"])
    )

    result = cursor.fetchone()
    return {"count_category": result["count_category"]}


@app.get("/expenses/sort-by-amount")
def sort_by_amount(
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    cursor = connection.execute(
        """
        SELECT * FROM expenses
        WHERE user_id = %s
        ORDER BY amount DESC
        """,
        (current_user["id"],)
    )

    return {"expenses": cursor.fetchall()}


@app.get("/expenses/filter-range")
def filter_range(
    min_amount: float = Query(ge=0),
    max_amount: float = Query(gt=0),
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    if min_amount > max_amount:
        raise HTTPException(
            status_code=400,
            detail="min_amount cannot be greater than max_amount"
        )

    cursor = connection.execute(
        """
        SELECT * FROM expenses
        WHERE amount >= %s AND amount <= %s AND user_id = %s
        """,
        (min_amount, max_amount, current_user["id"])
    )

    return {"expenses": cursor.fetchall()}


@app.get("/expenses/paginated")
def pagination(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    connection: psycopg.Connection = Depends(get_db)
):
    offset = (page - 1) * page_size

    count_cursor = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM expenses
        WHERE user_id = %s
        """,
        (current_user["id"],)
    )

    total_expenses = count_cursor.fetchone()["total"]
    total_pages = math.ceil(total_expenses / page_size)

    cursor = connection.execute(
        """
        SELECT * FROM expenses
        WHERE user_id = %s
        ORDER BY id
        LIMIT %s OFFSET %s
        """,
        (current_user["id"], page_size, offset)
    )

    return {
        "page": page,
        "page_size": page_size,
        "total_expenses": total_expenses,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "expenses": cursor.fetchall()
    }
