"""Adaptadores MRL · módulo Maintenance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterable

from app.activos_list_service import build_activos_list_items
from app.mrl.excel.exporter import BaseExcelExporter
from app.mrl.metadata import MRLDocumentMeta
from app.timezone_utils import resolve_timezone_name

if TYPE_CHECKING:
    from app.models import Empresa, Machine


def _usuario_label(usuario: str | object | None) -> str:
    if usuario is None:
        from app.mrl.constants import SYSTEM_USER

        return SYSTEM_USER
    if isinstance(usuario, str):
        return usuario.strip() or "Usuario"
    etiqueta = getattr(usuario, "etiqueta", None)
    if callable(etiqueta):
        return etiqueta()
    return str(getattr(usuario, "username", usuario) or "Usuario")


def _meta_activos(
    empresa: Empresa,
    *,
    usuario: str | object | None,
    batch_code: str | None = None,
) -> MRLDocumentMeta:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return MRLDocumentMeta(
        doc_code="DOC-010",
        instance_code=batch_code or f"ACTIVOS-{stamp}",
        module="Maintenance",
        title="Listado de activos",
        empresa_id=empresa.id,
        empresa_nombre=(empresa.razon_social or "Empresa").strip(),
        empresa_nit=(empresa.nit or "").strip() or None,
        generated_at=datetime.now(timezone.utc),
        timezone_name=resolve_timezone_name(empresa),
        usuario=_usuario_label(usuario),
    )


def activos_table_rows(machines: Iterable[Machine]) -> tuple[list[str], list[list]]:
    """Transforma activos del tenant en headers y filas tabulares."""
    items = build_activos_list_items(list(machines))
    headers = [
        "Código",
        "Nombre",
        "Tipo",
        "Ubicación",
        "Área",
        "Estado",
        "Criticidad",
        "Crítico",
        "Último mantenimiento",
        "Próximo mantenimiento",
    ]
    rows: list[list] = []
    for item in items:
        rows.append(
            [
                item["codigo"],
                item["nombre"],
                item["tipo_etiqueta"],
                item["ubicacion"],
                item["area"] or "—",
                item["status_label"],
                item["criticidad_label"],
                "Sí" if item["es_critico"] else "No",
                item["ultimo_mant"],
                item["proximo_mant"],
            ]
        )
    return headers, rows


def export_activos_excel(
    empresa: Empresa,
    machines: Iterable[Machine],
    *,
    usuario: str | object | None = None,
) -> tuple[bytes, str]:
    """Exporta listado de activos vía BaseExcelExporter."""
    meta = _meta_activos(empresa, usuario=usuario)
    headers, rows = activos_table_rows(machines)
    exporter = BaseExcelExporter(meta)
    sheet = exporter.add_sheet("Activos")
    sheet.write_table(headers, rows)
    return exporter.save()
