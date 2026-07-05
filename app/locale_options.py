"""Países, monedas y zonas horarias para registro y configuración de empresa."""

from __future__ import annotations

# clave interna, etiqueta visible, valor país guardado, moneda y zona por defecto
PAISES_ONBOARDING: tuple[tuple[str, str, str, str, str], ...] = (
    ("colombia", "Colombia", "Colombia", "COP", "America/Bogota"),
    ("mexico", "México", "México", "MXN", "America/Mexico_City"),
    ("peru", "Perú", "Perú", "USD", "America/Lima"),
    ("venezuela", "Venezuela", "Venezuela", "VES", "America/Caracas"),
    ("otro", "Otro", "", "USD", "America/Bogota"),
)

MONEDAS_LABELS: dict[str, str] = {
    "COP": "COP — Peso colombiano",
    "VES": "VES — Bolívar venezolano",
    "USD": "USD — Dólar estadounidense",
    "MXN": "MXN — Peso mexicano",
}

# Etiquetas al registrar una empresa en Venezuela (realidad multi-moneda)
MONEDAS_LABELS_VENEZUELA: dict[str, str] = {
    "USD": "USD — Dólares (uso comercial habitual)",
    "VES": "VES — Bolívares",
    "COP": "COP — Pesos colombianos (zona fronteriza)",
}

# Orden sugerido de moneda principal según país
MONEDAS_POR_PAIS: dict[str, tuple[str, ...]] = {
    "colombia": ("COP", "USD"),
    "mexico": ("MXN", "USD"),
    "peru": ("USD", "COP"),
    "venezuela": ("USD", "VES", "COP"),
    "otro": ("USD", "COP", "VES", "MXN"),
}

MONEDAS_ONBOARDING: tuple[tuple[str, str], ...] = tuple(
    (cod, MONEDAS_LABELS[cod]) for cod in ("COP", "VES", "USD", "MXN")
)

ZONAS_HORARIA_ONBOARDING: tuple[tuple[str, str], ...] = (
    ("America/Bogota", "America/Bogotá (Colombia)"),
    ("America/Caracas", "America/Caracas (Venezuela)"),
    ("America/Mexico_City", "America/Ciudad de México"),
    ("America/Lima", "America/Lima (Perú)"),
)

PAIS_CLAVES = frozenset(p[0] for p in PAISES_ONBOARDING)

from app.currency import MONEDAS_VENEZUELA  # noqa: E402  — evita import circular leve

NOTA_MONEDA_VENEZUELA = (
    "En Venezuela muchos negocios operan en dólares, bolívares y pesos colombianos (frontera). "
    "Puedes registrar precios y ventas en las tres monedas, o elegir solo una si así trabajas."
)

MODO_MONEDA_UNA = "una"
MODO_MONEDA_TRES = "tres"


def pais_preset_por_nombre(pais: str | None) -> str:
    nombre = (pais or "").strip().lower()
    for clave, _, valor, _, _ in PAISES_ONBOARDING:
        if valor and valor.lower() == nombre:
            return clave
    return "otro"


def defaults_pais_preset(clave: str | None) -> dict[str, str]:
    key = (clave or "colombia").strip().lower()
    for c, _, pais, moneda, zona in PAISES_ONBOARDING:
        if c == key:
            return {"pais": pais, "moneda": moneda, "zona_horaria": zona, "preset": c}
    return {"pais": "", "moneda": "USD", "zona_horaria": "America/Bogota", "preset": "otro"}


def zona_horaria_por_pais(pais: str | None) -> str | None:
    preset = pais_preset_por_nombre(pais)
    if preset == "otro" and not (pais or "").strip():
        return None
    return defaults_pais_preset(preset).get("zona_horaria")


def zona_horaria_label(zona: str | None) -> str:
    clave = (zona or "America/Bogota").strip()
    for val, label in ZONAS_HORARIA_ONBOARDING:
        if val == clave:
            return label
    return clave.replace("_", " ")


def monedas_para_pais(clave: str | None) -> list[tuple[str, str]]:
    """Opciones de moneda ordenadas según el país (Venezuela: USD, VES, COP)."""
    key = (clave or "").strip().lower()
    orden = MONEDAS_POR_PAIS.get(key, tuple(MONEDAS_LABELS.keys()))
    labels = MONEDAS_LABELS_VENEZUELA if key == "venezuela" else MONEDAS_LABELS
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for cod in orden:
        if cod in labels and cod not in seen:
            out.append((cod, labels[cod]))
            seen.add(cod)
    if key == "venezuela":
        return out
    for cod, lbl in MONEDAS_ONBOARDING:
        if cod not in seen:
            out.append((cod, lbl))
            seen.add(cod)
    return out


def paises_para_onboarding_json() -> list[dict]:
    out: list[dict] = []
    for c, label, pais, moneda, zona in PAISES_ONBOARDING:
        entry: dict = {
            "clave": c,
            "label": label,
            "pais": pais,
            "moneda": moneda,
            "zona_horaria": zona,
            "monedas": [{"codigo": cod, "label": lbl} for cod, lbl in monedas_para_pais(c)],
        }
        if c == "venezuela":
            entry["nota_moneda"] = NOTA_MONEDA_VENEZUELA
            entry["monedas_triple"] = list(MONEDAS_VENEZUELA)
        out.append(entry)
    return out
