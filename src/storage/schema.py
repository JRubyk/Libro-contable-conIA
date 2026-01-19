from src.storage.database import get_connection
from src.domain.accounts import ACCOUNTS
from src.domain.categories import CATEGORIES


# Se agrega mejora para saber si crédito es con cuotas.
def migrate_db() -> None:
    """Agrega columnas nuevas si la DB ya existía."""
    with get_connection() as conn:
        for sql in [
            "ALTER TABLE transactions ADD COLUMN installments INTEGER DEFAULT 0",
            "ALTER TABLE transactions ADD COLUMN interest_type TEXT DEFAULT 'none' "
            "CHECK (interest_type IN ('none','with_interest','without_interest'))",
        ]:
            try:
                conn.execute(sql)
            except Exception:
                # Ya existe la columna o SQLite no permite por alguna razón → ignorar
                pass


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL CHECK (type IN ('debit','credit','cash')),
                description TEXT,
                is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
            );

            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                kind TEXT NOT NULL CHECK (kind IN ('fixed','variable')),
                is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0,1))
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('expense','income','transfer','payment')),
                amount INTEGER NOT NULL CHECK (amount >= 0),
                account_from_id INTEGER,
                account_to_id INTEGER,
                category_id INTEGER,
                note TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(account_from_id) REFERENCES accounts(id),
                FOREIGN KEY(account_to_id) REFERENCES accounts(id),
                FOREIGN KEY(category_id) REFERENCES categories(id)
            );

            CREATE TABLE IF NOT EXISTS bot_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

    migrate_db()


def seed_defaults() -> None:
    with get_connection() as conn:
        # cuentas
        for name, data in ACCOUNTS.items():
            conn.execute(
                """
                INSERT OR IGNORE INTO accounts (name, type, description, is_active)
                VALUES (?, ?, ?, ?)
                """,
                (name, data["type"], data.get("description", ""), int(data.get("is_active", 1))),
            )

        # categorías
        for name, data in CATEGORIES.items():
            conn.execute(
                """
                INSERT OR IGNORE INTO categories (name, kind, is_active)
                VALUES (?, ?, 1)
                """,
                (name, data["kind"]),
            )
