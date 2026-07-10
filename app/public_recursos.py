"""Recursos públicos — stub MKT-09 · casos MTX-CASE (Sprint 14 · Fase 2)."""

from __future__ import annotations

RECURSOS_INTRO = (
    "Casos de transformación, guías comerciales y contenido para evaluar Maintix. "
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
        "titulo": "Manual comercial (MCM)",
        "desc": "Planes, sectores, demo y onboarding.",
        "href": "/mcm/",
        "icon": "bi-briefcase",
    },
    {
        "titulo": "Marketing (MKT)",
        "desc": "Landing, casos y materiales comerciales.",
        "href": "/mkt/",
        "icon": "bi-megaphone",
    },
    {
        "titulo": "Documentación técnica",
        "desc": "MRG, MUX y guías de producto.",
        "href": "/docs/",
        "icon": "bi-journal-code",
    },
)
