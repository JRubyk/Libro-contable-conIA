import re

def extract_installments_and_interest(text: str) -> tuple[int | None, str | None]:
    """
    Devuelve (cuotas, interest_type)
    interest_type: 'with_interest' | 'without_interest' | 'none'
    """
    t = text.lower()

    # cuotas: "3 cuotas", "en 3", "3x"
    m = re.search(r"\b(\d{1,2})\s*(cuotas|cuota|x)\b", t)
    if not m:
        m = re.search(r"\ben\s+(\d{1,2})\b", t)

    cuotas = int(m.group(1)) if m else None

    if "sin interes" in t or "sin interés" in t:
        return cuotas, "without_interest"
    if "con interes" in t or "con interés" in t:
        return cuotas, "with_interest"

    # si puso 0, asumimos none
    if cuotas == 0:
        return 0, "none"

    return cuotas, None
