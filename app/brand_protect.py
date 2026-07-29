"""Protección de nombres comerciales frente a traducción automática del navegador.

Corto plazo (piloto): `translate=\"no\"` + `class=\"notranslate\"` en marcas,
planes y módulos. Evita errores tipo Start → «Aviones» o Planes → «Aviones».

Mediano plazo: i18n propio (archivos de idioma). Ver docs/mkt/i18n-roadmap.md.
"""

from __future__ import annotations

import re
from typing import Iterable

from markupsafe import Markup, escape

# Orden: frases largas primero para no partir "Roustix Maintenance".
BRAND_TERMS: tuple[str, ...] = (
    "Roustix Maintenance",
    "Roustix Inventory",
    "Roustix Docs",
    "Todos los planes incluyen",
    "Roustix",
    "Enterprise",
    "Business",
    "Start",
    "Planes",  # ES: catálogo SaaS — evita traducción a «Aviones»
    "Purchasing",
    "Analytics",
    "CRM",
    "MAG",
    "MSD",
    "MCM",
    "MUX",
    "MDL",
    "MRG",
    "MPA",
    "MKT",
    "MBB",
    "MRL",
)

_ATTR = ' class="notranslate" translate="no"'


def wrap_notranslate(text: str | None) -> Markup:
    """Envuelve un nombre comercial completo (no traduce el contenido)."""
    if text is None:
        return Markup("")
    return Markup(f"<span{_ATTR}>{escape(str(text))}</span>")


def _ordered_terms(extra_terms: Iterable[str] | None = None) -> list[str]:
    terms = list(extra_terms or ()) + list(BRAND_TERMS)
    seen: set[str] = set()
    ordered: list[str] = []
    for t in terms:
        key = (t or "").strip()
        if key and key not in seen:
            seen.add(key)
            ordered.append(key)
    return ordered


def protect_brands(text: str | None, extra_terms: Iterable[str] | None = None) -> Markup:
    """Sustituye términos de marca conocidos por spans no traducibles."""
    if text is None or text == "":
        return Markup("")
    raw = str(text)
    ordered = _ordered_terms(extra_terms)
    if not ordered:
        return Markup(escape(raw))
    pattern = re.compile("|".join(re.escape(t) for t in ordered))
    parts: list[Markup] = []
    last = 0
    for match in pattern.finditer(raw):
        if match.start() > last:
            parts.append(Markup(escape(raw[last : match.start()])))
        parts.append(Markup(f"<span{_ATTR}>{escape(match.group(0))}</span>"))
        last = match.end()
    if last < len(raw):
        parts.append(Markup(escape(raw[last:])))
    return Markup("").join(parts)
