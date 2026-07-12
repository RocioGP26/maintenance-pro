"""Corrección defensiva de textos heredados con codificación dañada."""

from __future__ import annotations

import re


_PALABRAS_CON_ACENTO = {
    "acci?n": "acción",
    "administraci?n": "administración",
    "a?o": "año",
    "a?os": "años",
    "atenci?n": "atención",
    "c?digo": "código",
    "categor?a": "categoría",
    "cr?tica": "crítica",
    "cr?tico": "crítico",
    "descripci?n": "descripción",
    "direcci?n": "dirección",
    "el?ctrica": "eléctrica",
    "el?ctrico": "eléctrico",
    "ejecuci?n": "ejecución",
    "est?": "está",
    "facturaci?n": "facturación",
    "gesti?n": "gestión",
    "informaci?n": "información",
    "inspecci?n": "inspección",
    "intervenci?n": "intervención",
    "l?nea": "línea",
    "l?neas": "líneas",
    "lubricaci?n": "lubricación",
    "m?quina": "máquina",
    "m?quinas": "máquinas",
    "m?ndez": "méndez",
    "m?todo": "método",
    "n?mero": "número",
    "operaci?n": "operación",
    "organizaci?n": "organización",
    "observaci?n": "observación",
    "observaciones?": "observaciones",
    "planeaci?n": "planeación",
    "producci?n": "producción",
    "pr?ximo": "próximo",
    "pr?ximos": "próximos",
    "raz?n": "razón",
    "recepci?n": "recepción",
    "reparaci?n": "reparación",
    "revisi?n": "revisión",
    "secci?n": "sección",
    "situaci?n": "situación",
    "t?cnica": "técnica",
    "t?cnico": "técnico",
    "t?cnicos": "técnicos",
    "ubicaci?n": "ubicación",
    "v?lvula": "válvula",
    "v?lvulas": "válvulas",
}

_PATRON_PALABRAS = re.compile(
    "|".join(re.escape(k) for k in sorted(_PALABRAS_CON_ACENTO, key=len, reverse=True)),
    re.IGNORECASE,
)


def _respetar_mayusculas(original: str, corregido: str) -> str:
    if original.isupper():
        return corregido.upper()
    if original[:1].isupper():
        return corregido[:1].upper() + corregido[1:]
    return corregido


def texto_legible(valor):
    """Repara mojibake UTF-8 y palabras españolas guardadas con ``?``."""
    if not isinstance(valor, str) or not valor:
        return valor

    era_markup = type(valor).__name__ == "Markup"
    texto = str(valor).replace("\ufffd", "?")

    # Corrige secuencias típicas como ``UbicaciÃ³n`` o ``â€”``.
    for _ in range(2):
        if not any(marca in texto for marca in ("Ã", "Â", "â€", "â€”", "â€“")):
            break
        try:
            reparado = texto.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if reparado == texto:
            break
        texto = reparado

    def reemplazar(match: re.Match[str]) -> str:
        original = match.group(0)
        corregido = _PALABRAS_CON_ACENTO[original.lower()]
        return _respetar_mayusculas(original, corregido)

    texto = _PATRON_PALABRAS.sub(reemplazar, texto)
    if era_markup:
        from markupsafe import Markup

        return Markup(texto)
    return texto
