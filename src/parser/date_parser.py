import re
from datetime import date, timedelta

def extract_date_iso(text: str) -> str:
    t = text.lower().strip()
    today = date.today()

    if "hoy" in t:
        return today.isoformat()
    if "ayer" in t:
        return (today - timedelta(days=1)).isoformat()

    # dd/mm o dd-mm (asume año actual)
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", t)
    if m:
        d = int(m.group(1))
        mo = int(m.group(2))
        return date(today.year, mo, d).isoformat()

    return today.isoformat()
