from src.parser.message_parser import ParsedMessage
from src.storage.repository import insert_transaction

# códigos de resultado
OK = "ok"
UNKNOWN = "unknown"
MISSING_AMOUNT = "missing_amount"
MISSING_CATEGORY = "missing_category"
MISSING_ACCOUNT_TO = "missing_account_to"
NEEDS_INSTALLMENTS = "needs_installments"


def _is_credit_account(name: str | None) -> bool:
    return (name or "").lower() in ("credito", "tarjeta2")


def _normalize_interest(interest_type: str | None, installments: int) -> str:
    """
    interest_type permitido: none | with_interest | without_interest
    """
    if installments == 0:
        return "none"
    if interest_type in ("with_interest", "without_interest"):
        return interest_type
    # si hay cuotas y no especificó, asumimos sin interés (puedes cambiarlo si quieres)
    return "without_interest"


def apply_parsed_message(pm: ParsedMessage) -> tuple[bool, str, str, str]:
    """
    Retorna:
    (ok, mensaje, codigo, intent)
    """

    if pm.intent == "unknown":
        return False, "No entendí 😅 Intenta: 'hoy gasté 30000 en peluquería'.", UNKNOWN, pm.intent

    if pm.amount is None:
        return False, "Me faltó el monto 😅 Ej: 'hoy gasté 30000 en antojos'.", MISSING_AMOUNT, pm.intent

    # -------------------
    # GASTOS
    # -------------------
    if pm.intent == "expense":
        if not pm.category:
            return False, "Me faltó la categoría 😅 Ej: '... en verduras y frutas' o '... en servicios'.", MISSING_CATEGORY, pm.intent

        # 💳 Si es crédito, necesitamos cuotas antes de registrar
        if _is_credit_account(pm.account_from):
            if pm.installments is None:
                return (
                    False,
                    "💳 Veo que fue con crédito. ¿En cuántas cuotas fue?\n"
                    "Responde por ejemplo: `0` (sin cuotas) o `3 sin interes` o `12 con interes`.",
                    NEEDS_INSTALLMENTS,
                    pm.intent,
                )

            installments = int(pm.installments)
            interest_type = _normalize_interest(pm.interest_type, installments)

            insert_transaction(
                pm.date_iso,
                "expense",
                pm.amount,
                account_from=pm.account_from,
                category=pm.category,
                installments=installments,
                interest_type=interest_type,
                note=pm.note,
            )

            label_interest = {
                "none": "sin cuotas",
                "without_interest": "sin interés",
                "with_interest": "con interés",
            }.get(interest_type, interest_type)

            return (
                True,
                f"✅ Gasto crédito registrado: {pm.category} | ${pm.amount} | {installments} cuotas ({label_interest}) | {pm.date_iso}",
                OK,
                pm.intent,
            )

        # 🟢 No crédito: registrar normal
        insert_transaction(
            pm.date_iso,
            "expense",
            pm.amount,
            account_from=pm.account_from,
            category=pm.category,
            installments=0,
            interest_type="none",
            note=pm.note,
        )
        return True, f"✅ Gasto registrado: {pm.category} | ${pm.amount} | {pm.date_iso}", OK, pm.intent

    # -------------------
    # INGRESOS
    # -------------------
    if pm.intent == "income":
        insert_transaction(
            pm.date_iso,
            "income",
            pm.amount,
            account_from=pm.account_from,
            installments=0,
            interest_type="none",
            note=pm.note,
        )
        return True, f"✅ Ingreso registrado: ${pm.amount} | {pm.date_iso}", OK, pm.intent

    # -------------------
    # TRANSFERENCIAS / PAGOS
    # -------------------
    if pm.intent in ("transfer", "payment"):
        if not pm.account_to:
            return False, "Me faltó la cuenta destino 😅 Ej: 'transferí 200000 de debito a credito'.", MISSING_ACCOUNT_TO, pm.intent

        tx_type = "payment" if pm.intent == "payment" else "transfer"
        insert_transaction(
            pm.date_iso,
            tx_type,
            pm.amount,
            account_from=pm.account_from,
            account_to=pm.account_to,
            installments=0,
            interest_type="none",
            note=pm.note,
        )
        return True, f"✅ Movimiento registrado: {tx_type} | ${pm.amount} | {pm.account_from} → {pm.account_to}", OK, pm.intent

    return False, "No pude procesarlo 😅", UNKNOWN, pm.intent
