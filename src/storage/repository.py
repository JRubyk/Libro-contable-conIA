from src.storage.database import get_connection


def _get_id(table: str, name: str) -> int | None:
    with get_connection() as conn:
        row = conn.execute(f"SELECT id FROM {table} WHERE name = ?", (name,)).fetchone()
        return int(row["id"]) if row else None


def account_id(name: str) -> int | None:
    return _get_id("accounts", name)


def category_id(name: str) -> int | None:
    return _get_id("categories", name)


def insert_transaction(
    date_iso: str,
    tx_type: str,
    amount: int,
    account_from: str | None = None,
    account_to: str | None = None,
    category: str | None = None,
    installments: int = 0,
    interest_type: str = "none",
    note: str = "",
) -> int:
    af_id = account_id(account_from) if account_from else None
    at_id = account_id(account_to) if account_to else None
    cat_id = category_id(category) if category else None

    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO transactions (
                date, type, amount,
                account_from_id, account_to_id, category_id,
                note, installments, interest_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                date_iso, tx_type, amount,
                af_id, at_id, cat_id,
                note, int(installments), interest_type
            ),
        )
        return int(cur.lastrowid)


def get_month_summary(month_yyyy_mm: str) -> dict:
    """
    Retorna:
    - total gastos
    - total ingresos
    - total fixed/variable (según categoría)
    - totales por categoría
    """
    start = f"{month_yyyy_mm}-01"
    end = f"{month_yyyy_mm}-31"

    with get_connection() as conn:
        total_exp = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE type='expense' AND date BETWEEN ? AND ?",
            (start, end),
        ).fetchone()["s"]

        total_inc = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE type='income' AND date BETWEEN ? AND ?",
            (start, end),
        ).fetchone()["s"]

        fixed = conn.execute(
            """
            SELECT COALESCE(SUM(t.amount),0) AS s
            FROM transactions t
            JOIN categories c ON c.id=t.category_id
            WHERE t.type='expense' AND c.kind='fixed' AND t.date BETWEEN ? AND ?
            """,
            (start, end),
        ).fetchone()["s"]

        variable = conn.execute(
            """
            SELECT COALESCE(SUM(t.amount),0) AS s
            FROM transactions t
            JOIN categories c ON c.id=t.category_id
            WHERE t.type='expense' AND c.kind='variable' AND t.date BETWEEN ? AND ?
            """,
            (start, end),
        ).fetchone()["s"]

        by_cat = conn.execute(
            """
            SELECT c.name AS category, COALESCE(SUM(t.amount),0) AS total
            FROM transactions t
            JOIN categories c ON c.id=t.category_id
            WHERE t.type='expense' AND t.date BETWEEN ? AND ?
            GROUP BY c.name
            ORDER BY total DESC
            """,
            (start, end),
        ).fetchall()

    return {
        "month": month_yyyy_mm,
        "total_expenses": int(total_exp),
        "total_incomes": int(total_inc),
        "fixed_expenses": int(fixed),
        "variable_expenses": int(variable),
        "by_category": [(r["category"], int(r["total"])) for r in by_cat],
    }
