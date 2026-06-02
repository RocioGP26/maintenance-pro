"""Formato de montos según moneda de la empresa."""


def formato_moneda(valor, moneda: str = "COP") -> str:
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return "—"
    moneda = (moneda or "COP").upper()
    if moneda == "EUR":
        return f"€{n:,.2f}"
    if moneda == "USD":
        return f"${n:,.2f}"
    # COP y otras: miles con punto, decimales con coma
    entero, _, frac = f"{n:.2f}".partition(".")
    entero_fmt = f"{int(entero):,}".replace(",", ".")
    if frac == "00":
        return f"${entero_fmt}"
    return f"${entero_fmt},{frac}"
