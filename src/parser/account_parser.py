import re
from src.domain.keywords import ACCOUNT_KEYWORDS
from src.config import DEFAULT_ACCOUNT_NAME

def detect_account_single(text: str) -> str | None:
    t = text.lower()
    for acc, triggers in ACCOUNT_KEYWORDS.items():
        if any(w in t for w in triggers):
            return acc
    return None

def detect_transfer_accounts(text: str) -> tuple[str | None, str | None]:
    """
    Intenta detectar "del debito a la credito" / "de debito a credito".
    """
    t = text.lower()

    # patrón simple: de X a Y
    m = re.search(r"\bde\s+(\w+)\s+a\s+(\w+)\b", t)
    if m:
        return m.group(1), m.group(2)

    # patrón: del X a la Y
    m = re.search(r"\bdel\s+(\w+)\s+a\s+la\s+(\w+)\b", t)
    if m:
        return m.group(1), m.group(2)

    return None, None

def default_account() -> str:
    return DEFAULT_ACCOUNT_NAME
