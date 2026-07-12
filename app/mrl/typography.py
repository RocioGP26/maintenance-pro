"""Tipografía oficial MRL · MRL-04-HDR · MRL-STD §5."""

from __future__ import annotations

from dataclasses import dataclass

# Excel — fuente oficial
EXCEL_FONT_FAMILY = "Calibri"

# PDF — equivalente ReportLab embebido (Sprint 15.3+)
PDF_FONT_FAMILY = "Helvetica"
PDF_FONT_FAMILY_BOLD = "Helvetica-Bold"
PDF_FONT_FAMILY_OBLIQUE = "Helvetica-Oblique"


@dataclass(frozen=True)
class FontSize:
    """Tamaños en puntos."""

    title: int
    subtitle: int
    header: int
    body: int
    meta: int
    footer: int
    wordmark: int


# PDF
PDF_FONT_SIZES = FontSize(
    title=16,
    subtitle=12,
    header=11,
    body=11,
    meta=9,
    footer=8,
    wordmark=10,
)

# Excel
EXCEL_FONT_SIZES = FontSize(
    title=14,
    subtitle=12,
    header=11,
    body=11,
    meta=9,
    footer=8,
    wordmark=10,
)
