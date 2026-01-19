import re

def extract_amount(text: str) -> int | None:
    # Soporta: 30.000 / $30.000 / 30000 / 30 000
    m = re.search(r"(\$?\s*\d{1,3}(?:[.\s]\d{3})+|\$?\s*\d+)", text)
    if not m:
        return None
    raw = m.group(1)
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None
