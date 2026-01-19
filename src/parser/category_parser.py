from src.domain.keywords import CATEGORY_KEYWORDS

def detect_category(text: str) -> str | None:
    t = text.lower()
    for cat, triggers in CATEGORY_KEYWORDS.items():
        if any(w in t for w in triggers):
            return cat
    return None
