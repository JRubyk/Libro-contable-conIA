from datetime import date
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from src.bot.responses import HELP_TEXT
from src.parser.message_parser import parse_message
from src.parser.installments import extract_installments_and_interest
from src.services.transactions import apply_parsed_message, NEEDS_INSTALLMENTS
from src.services.reports import format_month_summary


def _installments_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("0 (sin cuotas)", callback_data="inst:0"),
            InlineKeyboardButton("3", callback_data="inst:3"),
            InlineKeyboardButton("6", callback_data="inst:6"),
            InlineKeyboardButton("12", callback_data="inst:12"),
        ],
        [InlineKeyboardButton("Otro…", callback_data="inst:other")],
    ]
    return InlineKeyboardMarkup(keyboard)


def _interest_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Sin interés", callback_data="int:without_interest"),
            InlineKeyboardButton("Con interés", callback_data="int:with_interest"),
        ],
        [InlineKeyboardButton("Sin cuotas", callback_data="int:none")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hola! Soy tu Libro Contable.\n"
        "Escribe /help para ver ejemplos.\n\n"
        "💡 Si alguna vez no respondo, es porque estoy offline. "
        "Cuando vuelva, proceso todo lo que me hayas escrito."
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT)


async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month = date.today().strftime("%Y-%m")
    await update.message.reply_text(format_month_summary(month))


async def mes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /mes AAAA-MM  (ej: /mes 2026-01)")
        return
    month = context.args[0].strip()
    await update.message.reply_text(format_month_summary(month))


async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id if update.effective_user else "?"
    username = update.effective_user.username if update.effective_user else "?"
    await update.message.reply_text(
        f"🪪 Tus IDs:\nchat_id: {chat_id}\nuser_id: {user_id}\nusername: @{username}"
    )


async def on_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.message.chat.id
    pending = context.application.bot_data.setdefault("pending_installments", {})

    if chat_id not in pending:
        await query.edit_message_text("No tengo nada pendiente 🙂")
        return

    pm = pending[chat_id]
    data = query.data or ""

    # ---------- Elegir cuotas ----------
    if data.startswith("inst:"):
        value = data.split(":", 1)[1]

        if value == "other":
            await query.edit_message_text(
                "Escribe el número de cuotas (ej: 5) o 0 si no hay cuotas."
            )
            return

        pm.installments = int(value)

        # Si 0 cuotas, registramos de una vez (sin interés)
        if pm.installments == 0:
            pm.interest_type = "none"
            ok, msg, code, intent = apply_parsed_message(pm)
            del pending[chat_id]
            await query.edit_message_text(msg)
            return

        # Si >0, pedir interés
        await query.edit_message_text(
            f"✅ Cuotas: {pm.installments}\nAhora elige interés:",
            reply_markup=_interest_keyboard(),
        )
        return

    # ---------- Elegir interés ----------
    if data.startswith("int:"):
        value = data.split(":", 1)[1]
        pm.interest_type = value

        ok, msg, code, intent = apply_parsed_message(pm)
        del pending[chat_id]
        await query.edit_message_text(msg)
        return


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    chat_id = update.effective_chat.id

    pending = context.application.bot_data.setdefault("pending_installments", {})

    # =========================
    # 1) Si estamos esperando cuotas (porque apretó "Otro…"), este mensaje es la respuesta
    # =========================
    if chat_id in pending:
        pm_pending = pending[chat_id]

        installments, interest_type = extract_installments_and_interest(text)
        if installments is None:
            await update.message.reply_text(
                "No entendí 😅 Escribe un número (ej: 5) o 0.\n"
                "También sirve: `3 sin interes` / `12 con interes`.",
                reply_to_message_id=update.message.message_id,
            )
            return

        pm_pending.installments = int(installments)
        pm_pending.interest_type = interest_type

        ok, msg, code, intent = apply_parsed_message(pm_pending)
        del pending[chat_id]

        await update.message.reply_text(
            msg if ok else ("No pude registrarlo 😅\n" + msg),
            reply_to_message_id=update.message.message_id,
        )
        return

    # =========================
    # 2) Proceso normal: parsear mensaje
    # =========================
    pm = parse_message(text)
    ok, msg, code, intent = apply_parsed_message(pm)

    processing_backlog = context.application.bot_data.get("processing_backlog", False)

    # =========================
    # 3) Backlog: no spamear OK, solo responder errores
    # =========================
    if processing_backlog:
        stats = context.application.bot_data.setdefault("backlog_stats", {
            "income_ok": 0,
            "expense_ok": 0,
            "transfer_ok": 0,
            "payment_ok": 0,
            "needs_attention": 0,
        })

        if ok:
            if intent == "income":
                stats["income_ok"] += 1
            elif intent == "expense":
                stats["expense_ok"] += 1
            elif intent == "transfer":
                stats["transfer_ok"] += 1
            elif intent == "payment":
                stats["payment_ok"] += 1
            return

        stats["needs_attention"] += 1
        await update.message.reply_text(
            "🕒 Estaba offline y procesé tu mensaje recién.\n" + msg,
            reply_to_message_id=update.message.message_id,
        )
        return

    # =========================
    # 4) En vivo: si necesita cuotas, guardar pendiente y mostrar botones
    # =========================
    if code == NEEDS_INSTALLMENTS:
        pending[chat_id] = pm
        await update.message.reply_text(
            "💳 Fue con crédito. Elige cuotas:",
            reply_markup=_installments_keyboard(),
            reply_to_message_id=update.message.message_id,
        )
        return

    # =========================
    # 5) En vivo: respuesta normal
    # =========================
    await update.message.reply_text(msg)


def build_handlers():
    return [
        CommandHandler("start", start),
        CommandHandler("help", help_cmd),
        CommandHandler("whoami", whoami),
        CommandHandler("resumen", resumen),
        CommandHandler("mes", mes),
        CallbackQueryHandler(on_callback),  # ✅ clicks de botones
        MessageHandler(filters.TEXT & ~filters.COMMAND, on_text),
    ]
