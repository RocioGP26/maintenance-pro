"""Fachada de estilos MRL · bloques reutilizables MRL-HDR/TBL/KPI/FTR."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.mrl import colors
from app.mrl import constants
from app.mrl import typography
from app.mrl.metadata import MRLDocumentMeta


@dataclass(frozen=True)
class HeaderStyle:
    block_id: str
    background: str
    title_color: str
    body_color: str
    meta_color: str
    wordmark_color: str
    separator_color: str
    separator_opacity: float
    font_family_excel: str
    font_family_pdf: str
    font_sizes_excel: typography.FontSize
    font_sizes_pdf: typography.FontSize
    logo_max_width_mm: float
    logo_max_height_mm: float


@dataclass(frozen=True)
class TableStyle:
    block_id: str
    header_background: str
    header_text: str
    body_text: str
    border_color: str
    zebra_background: str
    header_height_pt: float
    cell_padding_pt: float
    zebra_enabled: bool
    font_family_excel: str
    font_family_pdf: str
    font_size: int


@dataclass(frozen=True)
class KpiStyle:
    block_id: str
    background: str
    label_color: str
    value_color: str
    border_color: str
    min_width_mm: float
    padding_mm: float
    font_family_excel: str
    font_family_pdf: str
    label_font_size: int
    value_font_size: int


@dataclass(frozen=True)
class FooterStyle:
    block_id: str
    text_color: str
    wordmark_color: str
    font_family_excel: str
    font_family_pdf: str
    font_size: int
    generated_by_label: str
    mrl_version: str


class MRLStyle:
    """API principal de estilos · sin dependencia de openpyxl ni ReportLab."""

    @staticmethod
    def header(meta: MRLDocumentMeta | None = None) -> HeaderStyle:
        _ = meta  # reservado para variantes por DOC en sprints futuros
        return HeaderStyle(
            block_id=constants.BLOCK_HEADER,
            background=colors.WHITE,
            title_color=colors.PRIMARY,
            body_color=colors.BODY,
            meta_color=colors.MUTED,
            wordmark_color=colors.MUTED,
            separator_color=colors.PRIMARY,
            separator_opacity=constants.PDF_HEADER_SEPARATOR_OPACITY,
            font_family_excel=typography.EXCEL_FONT_FAMILY,
            font_family_pdf=typography.PDF_FONT_FAMILY,
            font_sizes_excel=typography.EXCEL_FONT_SIZES,
            font_sizes_pdf=typography.PDF_FONT_SIZES,
            logo_max_width_mm=constants.LOGO_MAX_WIDTH_MM,
            logo_max_height_mm=constants.LOGO_MAX_HEIGHT_MM,
        )

    @staticmethod
    def table() -> TableStyle:
        return TableStyle(
            block_id=constants.BLOCK_TABLE,
            header_background=colors.HEADER,
            header_text=colors.HEADER_TEXT,
            body_text=colors.BODY,
            border_color=colors.BORDER,
            zebra_background=colors.SURFACE,
            header_height_pt=constants.TABLE_HEADER_HEIGHT_PT,
            cell_padding_pt=constants.TABLE_CELL_PADDING_PT,
            zebra_enabled=constants.TABLE_ROW_ZEBRA,
            font_family_excel=typography.EXCEL_FONT_FAMILY,
            font_family_pdf=typography.PDF_FONT_FAMILY,
            font_size=typography.EXCEL_FONT_SIZES.body,
        )

    @staticmethod
    def kpi() -> KpiStyle:
        return KpiStyle(
            block_id=constants.BLOCK_KPI,
            background=colors.WHITE,
            label_color=colors.MUTED,
            value_color=colors.PRIMARY,
            border_color=colors.BORDER,
            min_width_mm=constants.KPI_CARD_MIN_WIDTH_MM,
            padding_mm=constants.KPI_CARD_PADDING_MM,
            font_family_excel=typography.EXCEL_FONT_FAMILY,
            font_family_pdf=typography.PDF_FONT_FAMILY,
            label_font_size=typography.EXCEL_FONT_SIZES.meta,
            value_font_size=typography.EXCEL_FONT_SIZES.title,
        )

    @staticmethod
    def footer(meta: MRLDocumentMeta | None = None) -> FooterStyle:
        version = meta.mrl_version if meta else constants.MRL_VERSION
        return FooterStyle(
            block_id=constants.BLOCK_FOOTER,
            text_color=colors.MUTED,
            wordmark_color=colors.MUTED,
            font_family_excel=typography.EXCEL_FONT_FAMILY,
            font_family_pdf=typography.PDF_FONT_FAMILY,
            font_size=typography.EXCEL_FONT_SIZES.footer,
            generated_by_label=constants.GENERATED_BY_LABEL,
            mrl_version=f"MRL v{version}",
        )

    @staticmethod
    def semantic_status(status: str) -> str:
        """Color semántico para estados operativos."""
        key = (status or "").strip().lower()
        if key in ("ok", "operativo", "disponible", "completado", "success"):
            return colors.SUCCESS
        if key in ("critico", "crítico", "vencido", "falla", "danger", "error"):
            return colors.DANGER
        if key in ("advertencia", "warning", "proximo", "próximo", "pendiente"):
            return colors.WARNING
        return colors.ACCENT

    @staticmethod
    def bundle(meta: MRLDocumentMeta) -> dict[str, Any]:
        """Paquete completo de estilos + metadata para un documento."""
        return {
            "meta": meta.as_dict(),
            "header": MRLStyle.header(meta),
            "table": MRLStyle.table(),
            "kpi": MRLStyle.kpi(),
            "footer": MRLStyle.footer(meta),
        }
