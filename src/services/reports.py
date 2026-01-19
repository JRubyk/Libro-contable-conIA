from src.storage.repository import get_month_summary

def format_month_summary(month: str) -> str:
    s = get_month_summary(month)
    lines = [
        f"📅 Resumen {s['month']}",
        f"💸 Gastos: ${s['total_expenses']}",
        f"💰 Ingresos: ${s['total_incomes']}",
        f"📌 Fijos: ${s['fixed_expenses']} | Variables: ${s['variable_expenses']}",
    ]

    if s["by_category"]:
        lines.append("\n📂 Por categoría:")
        for cat, total in s["by_category"]:
            lines.append(f"- {cat}: ${total}")
    else:
        lines.append("\n📭 No hay gastos categorizados ese mes todavía.")

    return "\n".join(lines)
