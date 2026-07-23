"""Recursos públicos — stub MKT-09 · casos MTX-CASE (Sprint 14 · Fase 2)."""

from __future__ import annotations

RECURSOS_INTRO = (
    "Guía de producto, brochure, casos de transformación y documentación para evaluar Roustix. "
    "El blog público llegará en una próxima versión del sitio."
)

MTX_CASES: tuple[dict[str, str], ...] = (
    {
        "codigo": "MTX-CASE-001",
        "titulo": "Industria Colombia",
        "sector": "Manufactura",
        "modulo": "Mantenimiento",
        "href": "/mkt/mtx-case/MTX-CASE-001-industria-colombia.md",
    },
    {
        "codigo": "MTX-CASE-002",
        "titulo": "Tornillería Venezuela",
        "sector": "Comercio",
        "modulo": "Inventario",
        "href": "/mkt/mtx-case/MTX-CASE-002-tornilleria-venezuela.md",
    },
    {
        "codigo": "MTX-CASE-003",
        "titulo": "Agroindustria",
        "sector": "Agro",
        "modulo": "Inventario o Mantenimiento",
        "href": "/mkt/mtx-case/MTX-CASE-003-agroindustria.md",
    },
    {
        "codigo": "MTX-CASE-004",
        "titulo": "Taller de mantenimiento",
        "sector": "Talleres",
        "modulo": "Mantenimiento",
        "href": "/mkt/mtx-case/MTX-CASE-004-taller-mantenimiento.md",
    },
    {
        "codigo": "MTX-CASE-005",
        "titulo": "Distribución",
        "sector": "Distribución",
        "modulo": "Inventario",
        "href": "/mkt/mtx-case/MTX-CASE-005-distribucion.md",
    },
    {
        "codigo": "MTX-CASE-006",
        "titulo": "Comercio multisede",
        "sector": "Operación mixta",
        "modulo": "Ambos módulos",
        "href": "/mkt/mtx-case/MTX-CASE-006-comercio-multisede.md",
    },
)

RECURSOS_LINKS: tuple[dict[str, str], ...] = (
    {
        "titulo": "Guía de producto",
        "desc": "Cómo funciona Roustix — mantenimiento e inventario.",
        "href": "/guia",
        "icon": "bi-journal-bookmark",
    },
    {
        "titulo": "Brochure corporativo",
        "desc": "8 páginas · imprimible / PDF (MKT-07).",
        "href": "/mkt/assets/brochure-corporativo.html",
        "icon": "bi-file-earmark-pdf",
    },
    {
        "titulo": "One Pager",
        "desc": "Resumen ejecutivo de una página.",
        "href": "/mkt/assets/one-pager.html",
        "icon": "bi-file-text",
    },
    {
        "titulo": "API y SDK",
        "desc": "MAG · MSD · OpenAPI para integradores.",
        "href": "/msd/",
        "icon": "bi-code-slash",
    },
    {
        "titulo": "Marketing (activos)",
        "desc": "Brochure, one pager y casos MTX-CASE.",
        "href": "/mkt/assets/brochure-corporativo.html",
        "icon": "bi-megaphone",
    },
    {
        "titulo": "Documentación pública",
        "desc": "Índice Roustix Docs (manuales públicos).",
        "href": "/docs/",
        "icon": "bi-journal-code",
    },
)
