"""Contenido público de demo comercial — MCM-07 (Sprint 14 · Fase 2)."""

from __future__ import annotations

DEMO_INTRO = (
    "Una demostración no es un tour de menú. Es mostrar cómo Maintix resuelve "
    "un problema real de operación en tu sector — en una sesión de 45–60 minutos "
    "con un flujo punta a punta."
)

DEMO_PLAYS: tuple[dict[str, str], ...] = (
    {
        "id": "PLAY-001",
        "title": "Preparación",
        "phase": "Antes de la reunión",
        "summary": (
            "Revisamos tu sector, el módulo de entrada (Mantenimiento o Inventario) "
            "y quién participará. Sin abrir pantallas todavía."
        ),
    },
    {
        "id": "PLAY-002",
        "title": "Descubrimiento",
        "phase": "Apertura · ~3 min",
        "summary": (
            "Entendemos tu dolor operativo y contamos la historia de tu sector "
            "antes de entrar al producto — mínimo tres preguntas clave."
        ),
    },
    {
        "id": "PLAY-003",
        "title": "Demo principal",
        "phase": "Operación · 10–15 min",
        "summary": (
            "Un solo flujo punta a punta: activo → OT, o producto → venta. "
            "Seguimos la historia, no el menú lateral."
        ),
    },
    {
        "id": "PLAY-004",
        "title": "Indicadores",
        "phase": "KPIs · ~3 min",
        "summary": (
            "Abrimos el dashboard del perfil decisor y señalamos uno o dos KPIs "
            "prioritarios para tu operación."
        ),
    },
    {
        "id": "PLAY-005",
        "title": "Cierre",
        "phase": "Siguiente paso · ~5 min",
        "summary": (
            "Plan recomendado, prueba gratuita de 15 días si aplica y fecha "
            "concreta de seguimiento — sin prometer módulos en roadmap."
        ),
    },
)
