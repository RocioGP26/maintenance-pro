"""Tokens de color oficiales MRL · MRL-07-COL."""

from __future__ import annotations

# Primarios MDL / MRL
PRIMARY = "#042C53"
SECONDARY = "#185FA5"
BODY = "#444441"
MUTED = "#888780"
ACCENT = "#185FA5"
BORDER = "#E2E8F0"
SURFACE = "#F4F7FB"
WHITE = "#FFFFFF"

# Semánticos operativos
SUCCESS = "#38A169"
WARNING = "#D69E2E"
DANGER = "#E53E3E"

# Alias de uso frecuente en exportadores
GRAY = MUTED
HEADER = PRIMARY
HEADER_TEXT = WHITE

# Registro público inmutable
ALL_COLORS: frozenset[str] = frozenset(
    {
        PRIMARY,
        SECONDARY,
        BODY,
        MUTED,
        ACCENT,
        BORDER,
        SURFACE,
        WHITE,
        SUCCESS,
        WARNING,
        DANGER,
    }
)
