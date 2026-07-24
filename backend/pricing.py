from typing import Optional

# Deben coincidir exactamente con las opciones de frontend/src/App.jsx
# (salesRangeCopOptions / salesRangeUsdOptions).
SALES_RANGE_COP_OPTIONS = [
    "Menos de 1.000",
    "Entre 1.001 y 5.000",
    "Entre 5.001 y 10.000",
    "Entre 10.001 y 90.000",
    "Mas de 90.000",
]

SALES_RANGE_USD_OPTIONS = [
    "Menos de 0,3",
    "Entre 0,3 y 1,5",
    "Entre 1,5 y 5,0",
    "Entre 5,0 y 25,0",
    "Mas de 25,0",
]

# Tabla de precios IDEUSS Agencia IA — Metodologia OOIA (Fase 1), en USD.
# Emparejada por posicion (tier 1..5) contra cualquiera de las dos listas de
# arriba: la tabla de precios para clientes fuera de Colombia reutiliza las
# mismas etiquetas de rango que la tabla en COP en el PDF fuente, lo cual
# parece un error de copiado (implicaria "menos de 1.000 millones de USD" en
# ventas). Los 5 precios si forman una progresion clara de 5 escalones, asi
# que se usan en el mismo orden sin importar la moneda.
PRICING_TIERS = [
    {"area_1": 1500, "area_4": 4000, "produccion_addon": 1000},
    {"area_1": 2500, "area_4": 8000, "produccion_addon": 2000},
    {"area_1": 3500, "area_4": 10000, "produccion_addon": 3000},
    {"area_1": 4500, "area_4": 14000, "produccion_addon": 4000},
    {"area_1": 5500, "area_4": 20000, "produccion_addon": 5000},
]


def get_pricing(moneda: str, rango_ventas: str) -> Optional[dict]:
    """Retorna {'area_1', 'area_4', 'produccion_addon'} en USD segun la moneda y el rango de ventas anuales reportado, o None si no hay match."""
    options = SALES_RANGE_USD_OPTIONS if moneda == "USD" else SALES_RANGE_COP_OPTIONS
    try:
        idx = options.index(rango_ventas)
    except ValueError:
        return None
    return PRICING_TIERS[idx]
