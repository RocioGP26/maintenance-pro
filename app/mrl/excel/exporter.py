"""Motor Excel MRL · BaseExcelExporter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from typing import Any, Literal

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.mrl import constants
from app.mrl.constants import SYSTEM_USER
from app.mrl.excel.autofit import auto_fit_columns
from app.mrl.excel.formatting import (
    apply_body_cell,
    apply_footer_row,
    apply_table_header_row,
)
from app.mrl.excel.utils import filename_for_meta, meta_generated_at
from app.mrl.excel.worksheet import (
    apply_auto_filter,
    freeze_below_header,
    write_institutional_header,
)
from app.mrl.metadata import MRLDocumentMeta
from app.mrl.styles import MRLStyle, TableStyle
from app.mrl.utils.dates import format_datetime_latam

ColumnKind = Literal["text", "date", "number", "integer", "currency"]

_NUMBER_FORMATS: dict[ColumnKind, str] = {
    "text": "General",
    "date": "DD/MM/YYYY",
    "number": "#,##0.00",
    "integer": "#,##0",
    "currency": '#,##0.00 "_"',
}


@dataclass(frozen=True)
class ColumnFormat:
    kind: ColumnKind = "text"
    number_format: str | None = None

    def resolved_format(self) -> str | None:
        if self.number_format:
            return self.number_format
        fmt = _NUMBER_FORMATS.get(self.kind, "General")
        return None if fmt == "General" else fmt


class ExcelSheetContext:
    """Handle de hoja para encadenar operaciones sin exponer openpyxl."""

    def __init__(self, exporter: BaseExcelExporter, ws: Worksheet, name: str) -> None:
        self._exporter = exporter
        self._ws = ws
        self.name = name

    def write_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        *,
        column_formats: list[ColumnFormat | ColumnKind | None] | None = None,
        apply_filter: bool = True,
        freeze_panes: bool = True,
        auto_fit: bool = True,
        include_footer: bool = True,
    ) -> int:
        return self._exporter._write_table(
            self._ws,
            headers,
            rows,
            column_formats=column_formats,
            apply_filter=apply_filter,
            freeze_panes=freeze_panes,
            auto_fit=auto_fit,
            include_footer=include_footer,
        )


class BaseExcelExporter:
    """
    Exportador Excel reutilizable · no conoce módulos de negocio.

    Uso típico::

        exporter = BaseExcelExporter(meta)
        sheet = exporter.add_sheet("Activos")
        sheet.write_table(headers, rows)
        content, filename = exporter.save()
    """

    def __init__(self, meta: MRLDocumentMeta) -> None:
        self._meta = meta
        self._wb = Workbook()
        self._default_sheet = self._wb.active
        self._default_sheet.title = "Sheet"
        self._sheets: list[ExcelSheetContext] = []
        self._used_default = False

    @classmethod
    def create(
        cls,
        *,
        title: str,
        doc_code: str,
        instance_code: str,
        module: str,
        empresa_id: int,
        empresa_nombre: str,
        timezone_name: str = "America/Bogota",
        usuario: str = SYSTEM_USER,
        empresa_nit: str | None = None,
        generated_at: datetime | None = None,
        locale: str = "es-CO",
        template: str | None = None,
    ) -> BaseExcelExporter:
        """Factory desde contexto tenant · sin modelos de negocio."""
        meta = MRLDocumentMeta(
            doc_code=doc_code,
            instance_code=instance_code,
            module=module,
            title=title,
            empresa_id=empresa_id,
            empresa_nombre=empresa_nombre,
            empresa_nit=empresa_nit,
            generated_at=generated_at or meta_generated_at(),
            timezone_name=timezone_name,
            usuario=usuario,
            locale=locale,
            template=template,
        )
        return cls(meta)

    @property
    def meta(self) -> MRLDocumentMeta:
        return self._meta

    def add_sheet(self, name: str) -> ExcelSheetContext:
        """Añade una hoja al workbook."""
        safe_name = (name or "Export")[:31]
        if not self._used_default:
            ws = self._default_sheet
            ws.title = safe_name
            self._used_default = True
        else:
            ws = self._wb.create_sheet(title=safe_name)
        ctx = ExcelSheetContext(self, ws, safe_name)
        self._sheets.append(ctx)
        return ctx

    def write_table(
        self,
        headers: list[str],
        rows: list[list[Any]],
        **kwargs: Any,
    ) -> int:
        """Escribe tabla en la última hoja añadida."""
        if not self._sheets:
            raise RuntimeError("Debe llamar add_sheet() antes de write_table()")
        return self._sheets[-1].write_table(headers, rows, **kwargs)

    def _write_table(
        self,
        ws: Worksheet,
        headers: list[str],
        rows: list[list[Any]],
        *,
        column_formats: list[ColumnFormat | ColumnKind | None] | None = None,
        apply_filter: bool = True,
        freeze_panes: bool = True,
        auto_fit: bool = True,
        include_footer: bool = True,
        table_style: TableStyle | None = None,
    ) -> int:
        style = table_style or MRLStyle.table()
        num_cols = max(len(headers), 1)
        write_institutional_header(ws, self._meta, num_cols)
        header_row = constants.EXCEL_HEADER_ROW
        apply_table_header_row(ws, header_row, headers, style)

        formats = _normalize_column_formats(column_formats, len(headers))
        data_start = constants.EXCEL_DATA_START_ROW
        for row_offset, row_values in enumerate(rows):
            excel_row = data_start + row_offset
            zebra = row_offset % 2 == 1
            for col_idx, value in enumerate(row_values, start=1):
                fmt = formats[col_idx - 1] if col_idx - 1 < len(formats) else ColumnFormat()
                apply_body_cell(
                    ws,
                    excel_row,
                    col_idx,
                    value,
                    table_style=style,
                    zebra=zebra,
                    number_format=fmt.resolved_format(),
                )

        last_data_row = data_start + len(rows) - 1 if rows else header_row
        footer_row = last_data_row + 1

        if include_footer and rows:
            footer_row = last_data_row + 2
            fecha = format_datetime_latam(
                self._meta.generated_at, self._meta.timezone_name
            )
            footer = (
                f"{constants.GENERATED_BY_LABEL} · MRL v{self._meta.mrl_version} · {fecha}"
            )
            apply_footer_row(ws, footer_row, footer, num_cols=num_cols)

        if freeze_panes:
            freeze_below_header(ws)
        if apply_filter and rows:
            apply_auto_filter(ws, header_row, last_data_row, num_cols)
        if auto_fit:
            auto_fit_columns(
                ws,
                num_cols,
                first_row=constants.EXCEL_META_START_ROW,
                last_row=footer_row if include_footer and rows else last_data_row,
            )
        return last_data_row

    def save(self) -> tuple[bytes, str]:
        """Serializa el workbook a bytes y nombre de archivo MRL."""
        if not self._sheets:
            self.add_sheet("Export")
        buf = BytesIO()
        self._wb.save(buf)
        return buf.getvalue(), filename_for_meta(self._meta)


def _normalize_column_formats(
    specs: list[ColumnFormat | ColumnKind | None] | None,
    width: int,
) -> list[ColumnFormat]:
    if not specs:
        return [ColumnFormat()] * width
    result: list[ColumnFormat] = []
    for idx in range(width):
        if idx >= len(specs) or specs[idx] is None:
            result.append(ColumnFormat())
            continue
        item = specs[idx]
        if isinstance(item, ColumnFormat):
            result.append(item)
        else:
            result.append(ColumnFormat(kind=item))
    return result


# Alias público acordado en Sprint 15.2
ExcelExporter = BaseExcelExporter

__all__ = [
    "BaseExcelExporter",
    "ExcelExporter",
    "ExcelSheetContext",
    "ColumnFormat",
    "ColumnKind",
]
