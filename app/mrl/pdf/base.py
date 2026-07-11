"""Builders visuales ReportLab para el motor PDF MRL."""

from __future__ import annotations

from typing import Sequence

from reportlab.lib import colors as rl_colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, Table, TableStyle as RLTableStyle

from app.mrl import colors, typography
from app.mrl.styles import MRLStyle


def pdf_color(value: str):
    """Convierte un token hexadecimal MRL a color ReportLab."""
    return rl_colors.HexColor(value)


def paragraph_styles() -> dict[str, ParagraphStyle]:
    sizes = typography.PDF_FONT_SIZES
    return {
        "body": ParagraphStyle(
            "MRLBody", fontName=typography.PDF_FONT_FAMILY,
            fontSize=sizes.body, leading=sizes.body + 3,
            textColor=pdf_color(colors.BODY),
        ),
        "title": ParagraphStyle(
            "MRLTitle", fontName=f"{typography.PDF_FONT_FAMILY}-Bold",
            fontSize=sizes.title, leading=sizes.title + 3,
            textColor=pdf_color(colors.PRIMARY), spaceAfter=4 * mm,
        ),
        "table_header": ParagraphStyle(
            "MRLTableHeader", fontName=f"{typography.PDF_FONT_FAMILY}-Bold",
            fontSize=sizes.meta, leading=sizes.meta + 2,
            textColor=pdf_color(colors.WHITE), alignment=TA_LEFT,
        ),
        "table_cell": ParagraphStyle(
            "MRLTableCell", fontName=typography.PDF_FONT_FAMILY,
            fontSize=sizes.meta, leading=sizes.meta + 2,
            textColor=pdf_color(colors.BODY),
        ),
        "kpi_label": ParagraphStyle(
            "MRLKpiLabel", fontName=typography.PDF_FONT_FAMILY,
            fontSize=sizes.meta, leading=sizes.meta + 2,
            textColor=pdf_color(colors.MUTED), alignment=TA_CENTER,
        ),
        "kpi_value": ParagraphStyle(
            "MRLKpiValue", fontName=f"{typography.PDF_FONT_FAMILY}-Bold",
            fontSize=sizes.title, leading=sizes.title + 2,
            textColor=pdf_color(colors.PRIMARY), alignment=TA_CENTER,
        ),
    }


def build_table(
    headers: Sequence[object], rows: Sequence[Sequence[object]], *,
    column_widths: Sequence[float] | None = None,
) -> Table:
    """Construye MRL-TBL-001 sin conocer modelos de negocio."""
    styles = paragraph_styles()
    data = [[Paragraph(str(value), styles["table_header"]) for value in headers]]
    data.extend(
        [Paragraph("" if value is None else str(value), styles["table_cell"]) for value in row]
        for row in rows
    )
    table = Table(data, colWidths=column_widths, repeatRows=1, hAlign="LEFT")
    token = MRLStyle.table()
    commands = [
        ("BACKGROUND", (0, 0), (-1, 0), pdf_color(token.header_background)),
        ("GRID", (0, 0), (-1, -1), 0.35, pdf_color(token.border_color)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), token.cell_padding_pt),
        ("BOTTOMPADDING", (0, 0), (-1, -1), token.cell_padding_pt),
        ("LEFTPADDING", (0, 0), (-1, -1), token.cell_padding_pt),
        ("RIGHTPADDING", (0, 0), (-1, -1), token.cell_padding_pt),
    ]
    for index in range(2, len(data), 2):
        commands.append(("BACKGROUND", (0, index), (-1, index), pdf_color(token.zebra_background)))
    table.setStyle(RLTableStyle(commands))
    return table


def build_kpi_row(items: Sequence[tuple[str, object]]) -> Table:
    """Construye una fila de tarjetas MRL-KPI-001."""
    styles = paragraph_styles()
    cells = [
        [Paragraph(str(value), styles["kpi_value"]), Paragraph(label, styles["kpi_label"])]
        for label, value in items
    ]
    table = Table([cells], hAlign="LEFT")
    token = MRLStyle.kpi()
    table.setStyle(RLTableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), pdf_color(token.background)),
        ("BOX", (0, 0), (-1, -1), 0.5, pdf_color(token.border_color)),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, pdf_color(token.border_color)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), token.padding_mm * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), token.padding_mm * mm),
    ]))
    return table


__all__ = ["build_kpi_row", "build_table", "paragraph_styles", "pdf_color"]
