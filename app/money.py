"""Formato de montos según moneda de la empresa."""

MONEDAS_SOPORTADAS: tuple[tuple[str, str], ...] = (
    ("COP", "COP — Peso colombiano"),
    ("USD", "USD — Dólar estadounidense"),
    ("MXN", "MXN — Peso mexicano"),
)
MONEDAS_CODIGOS = frozenset(c for c, _ in MONEDAS_SOPORTADAS)

# Alias usado en configuración de empresa
MONEDAS_EMPRESA = MONEDAS_SOPORTADAS


def normalizar_moneda(codigo: str | None, default: str = "COP") -> str:
    c = (codigo or default).strip().upper()
    return c if c in MONEDAS_CODIGOS else (default if default in MONEDAS_CODIGOS else "COP")


def simbolo_moneda_input(moneda: str) -> str:
    """Prefijo corto para el campo de valor en formularios."""
    m = normalizar_moneda(moneda)
    if m == "USD":
        return "US$"
    if m == "MXN":
        return "MX$"
    if m == "EUR":
        return "€"
    return "$"


def formatear_monto_sin_simbolo(valor, moneda: str = "COP") -> str:
    """Monto para campo de texto (sin símbolo de moneda)."""
    try:
        n = float(valor)
    except (TypeError, ValueError):
        return ""
    moneda = normalizar_moneda(moneda)
    if moneda == "USD":
        entero, _, frac = f"{n:.2f}".partition(".")
        entero_fmt = f"{int(entero):,}"
        if frac == "00":
            return entero_fmt
        return f"{entero_fmt}.{frac}"
    entero, _, frac = f"{n:.2f}".partition(".")
    entero_fmt = f"{int(entero):,}".replace(",", ".")
    if frac == "00":
        return entero_fmt
    return f"{entero_fmt},{frac}"


def parsear_monto_form(texto: str | None, moneda: str = "COP") -> float | None:
    """Convierte texto con separadores de miles a número."""
    s = (texto or "").strip()
    if not s:
        return None
    moneda = normalizar_moneda(moneda)
    try:
        if moneda == "USD":
            return float(s.replace(",", ""))
        if "," in s:
            entero, _, frac = s.rpartition(",")
            entero = entero.replace(".", "")
            return float(f"{entero}.{frac}" if frac else entero)
        return float(s.replace(".", ""))
    except ValueError:
        return None


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
