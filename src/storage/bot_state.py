from src.storage.database import get_connection

KEY_LAST_UPDATE_ID = "last_update_id"


def get_last_update_id() -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT value FROM bot_state WHERE key = ?",
            (KEY_LAST_UPDATE_ID,),
        ).fetchone()
        return int(row["value"]) if row else 0


def set_last_update_id(update_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO bot_state (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
            """,
            (KEY_LAST_UPDATE_ID, str(update_id)),
        )
