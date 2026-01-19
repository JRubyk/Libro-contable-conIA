from typing import Dict

DEBIT = "debit"
CREDIT = "credit"
CASH = "cash"

ACCOUNTS: Dict[str, dict] = {
    "debito": {"type": DEBIT, "is_active": 1, "description": "Cuenta débito / Cuenta RUT"},
    "credito": {"type": CREDIT, "is_active": 1, "description": "Tarjeta de crédito principal"},
    "tarjeta2": {"type": CREDIT, "is_active": 0, "description": "Segunda tarjeta de crédito"},
    "efectivo": {"type": CASH, "is_active": 1, "description": "Dinero en efectivo"},
}
