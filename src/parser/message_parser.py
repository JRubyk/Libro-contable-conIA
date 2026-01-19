from dataclasses import dataclass
from src.parser.intent import detect_intent
from src.parser.amount import extract_amount
from src.parser.date_parser import extract_date_iso
from src.parser.category_parser import detect_category
from src.parser.account_parser import detect_account_single, detect_transfer_accounts, default_account

@dataclass
class ParsedMessage:
    intent: str
    date_iso: str
    amount: int | None
    category: str | None
    account_from: str | None
    account_to: str | None
    note: str
    installments: int | None
    interest_type: str | None


def parse_message(text: str) -> ParsedMessage:
    intent = detect_intent(text)
    date_iso = extract_date_iso(text)
    amount = extract_amount(text)
    category = detect_category(text)
    note = text.strip()
    inst, interest = extract_installments_and_interest(text)


    acc_from = None
    acc_to = None

    if intent in ("transfer", "payment"):
        a_from, a_to = detect_transfer_accounts(text)
        acc_from = a_from
        acc_to = a_to
        # si no detecta, al menos usa default en from
        if not acc_from:
            acc_from = default_account()
    else:
        acc_from = detect_account_single(text) or default_account()

    return ParsedMessage(
        intent=intent,
        date_iso=date_iso,
        amount=amount,
        category=category,
        account_from=acc_from,
        account_to=acc_to,
        note=note,
        installments=inst,
        interest_type=interest,

    )
from src.parser.installments import extract_installments_and_interest
