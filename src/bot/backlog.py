from datetime import date
from telegram.ext import Application

from src.storage.bot_state import get_last_update_id, set_last_update_id
from src.config import OWNER_CHAT_ID
from src.services.reports import format_month_summary



from datetime import date
from telegram.ext import Application

from src.storage.bot_state import get_last_update_id, set_last_update_id
from src.config import OWNER_CHAT_ID


async def process_backlog(app: Application, limit: int = 500) -> int:
    last_id = get_last_update_id()
    offset = last_id + 1 if last_id else None

    app.bot_data["processing_backlog"] = True
    app.bot_data["backlog_stats"] = {
        "income_ok": 0,
        "expense_ok": 0,
        "transfer_ok": 0,
        "payment_ok": 0,
        "needs_attention": 0,
    }

    updates = await app.bot.get_updates(offset=offset, limit=limit, timeout=1)
    if not updates:
        app.bot_data["processing_backlog"] = False
        return 0

    for upd in updates:
        await app.process_update(upd)

    set_last_update_id(updates[-1].update_id)

    stats = app.bot_data.get("backlog_stats", {})
    app.bot_data["processing_backlog"] = False

    # ✅ Resumen solo para ti (OWNER_CHAT_ID)
    if OWNER_CHAT_ID:
        resumen = (
            "📥 Backlog procesado\n"
            f"✅ Ingresos: {stats.get('income_ok', 0)}\n"
            f"✅ Gastos: {stats.get('expense_ok', 0)}\n"
            f"✅ Transferencias: {stats.get('transfer_ok', 0)}\n"
            f"✅ Pagos: {stats.get('payment_ok', 0)}\n"
            f"⚠️ Con datos faltantes: {stats.get('needs_attention', 0)}"
        )
        await app.bot.send_message(chat_id=OWNER_CHAT_ID, text=resumen)

    return len(updates)

