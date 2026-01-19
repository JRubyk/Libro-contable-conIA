def detect_intent(text: str) -> str:
    t = text.lower()

    if any(w in t for w in ["transferi", "transferí", "transferencia", "pasé", "pase", "moví", "movi"]):
        return "transfer"
    if any(w in t for w in ["pague la tarjeta", "pagué la tarjeta", "pago tarjeta", "pagué tarjeta", "pague tarjeta"]):
        return "payment"
    if any(w in t for w in ["me llegó", "me llego", "recibí", "recibi", "ingresó", "ingreso", "me pagaron", "sueldo"]):
        return "income"
    if any(w in t for w in ["gasté", "gaste", "compré", "compre", "pagué", "pague"]):
        return "expense"

    return "unknown"
