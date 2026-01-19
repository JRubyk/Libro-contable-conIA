from typing import Dict

FIXED = "fixed"
VARIABLE = "variable"

CATEGORIES: Dict[str, dict] = {
    # Gastos fijos
    "Alacena": {"kind": FIXED},
    "Verduras y frutas": {"kind": FIXED},
    "Proteinas": {"kind": FIXED},
    "Articulos de aseo": {"kind": FIXED},
    "Articulos de limpieza personal": {"kind": FIXED},
    "Medicina y medicamentos": {"kind": FIXED},
    "Servicios": {"kind": FIXED},
    "Suscripciones y planes": {"kind": FIXED},

    # Gastos variables
    "Antojos": {"kind": VARIABLE},
    "Videojuegos": {"kind": VARIABLE},
    "Emergencia medica": {"kind": VARIABLE},
    "Peluqueria": {"kind": VARIABLE},
    "Paseo y viajes": {"kind": VARIABLE},   
}
