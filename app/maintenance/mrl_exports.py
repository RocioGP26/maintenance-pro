"""Adaptadores MRL · módulo Maintenance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Iterable

from app.activos_list_service import build_activos_list_items
from app.mrl.excel.exporter import BaseExcelExporter
from app.mrl.metadata import MRLDocumentMeta
from app.timezone_utils import resolve_timezone_name

if TYPE_CHECKING:
    from app.models import Empresa, Machine, WorkOrder


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


def export_ordenes_excel(empresa: Empresa, orders: Iterable, *, usuario=None):
    """Exporta la vista filtrada de OT usando DOC-010."""
    from app.models import WORK_ORDER_PRIORITIES, wo_status_meta, wo_tipo_meta

    meta = MRLDocumentMeta(
        doc_code="DOC-010", instance_code=f"OT-{datetime.now(timezone.utc):%Y%m%d}",
        module="Maintenance", title="Órdenes de trabajo", empresa_id=empresa.id,
        empresa_nombre=(empresa.razon_social or "Empresa").strip(),
        empresa_nit=(empresa.nit or "").strip() or None,
        generated_at=datetime.now(timezone.utc), timezone_name=resolve_timezone_name(empresa),
        usuario=_usuario_label(usuario),
    )
    headers = ["Número", "Actividad", "Activo", "Área", "Ubicación", "Tipo", "Estado", "Prioridad", "Programada", "Inicio", "Cierre", "Tiempo", "Técnico"]
    priorities = dict(WORK_ORDER_PRIORITIES)
    rows = [[o.numero or f"#{o.id}", o.titulo, f"{o.machine.codigo} · {o.machine.nombre}" if o.machine else "—", o.area or getattr(o.machine, "area", "") or "—", o.ubicacion or getattr(o.machine, "ubicacion", "") or "—", wo_tipo_meta(o.tipo)["label"], wo_status_meta(o.status)["label"], priorities.get(o.prioridad, o.prioridad), o.fecha_programada, o.fecha_inicio, o.fecha_cierre, o.tiempo_gastado_label, o.technician.nombre if o.technician else "—"] for o in orders]
    exporter = BaseExcelExporter(meta)
    exporter.add_sheet("Órdenes").write_table(headers, rows, column_formats=[None] * 8 + ["date", "date", "date"] + [None, None])
    return exporter.save()


def _fecha(value, *, with_time: bool = False) -> str:
    if not value:
        return "—"
    return value.strftime("%d/%m/%Y %H:%M" if with_time else "%d/%m/%Y")


def _money(value, currency: str) -> str:
    if value is None:
        return "—"
    return f"{float(value):,.2f} {currency}"


def export_orden_trabajo_pdf(
    empresa: Empresa,
    work_order: WorkOrder,
    *,
    usuario: str | object | None = None,
    watermark: str | None = None,
) -> tuple[bytes, str]:
    """Genera DOC-001 sin acoplar el motor MRL a modelos de Maintenance."""
    from app.models import WORK_ORDER_PRIORITIES, wo_status_meta, wo_tipo_meta
    from app.mrl.pdf.exporter import BasePdfExporter

    numero = (work_order.numero or f"OT-{work_order.id}").strip()
    meta = MRLDocumentMeta(
        doc_code="DOC-001",
        instance_code=numero,
        module="Maintenance",
        title=f"Orden de Trabajo · {numero}",
        empresa_id=empresa.id,
        empresa_nombre=(empresa.razon_social or "Empresa").strip(),
        empresa_nit=(empresa.nit or "").strip() or None,
        generated_at=datetime.now(timezone.utc),
        timezone_name=resolve_timezone_name(empresa),
        usuario=_usuario_label(usuario),
        template="MRL-TPL-002",
    )
    exporter = BasePdfExporter(meta, watermark=watermark)
    status = wo_status_meta(work_order.status)["label"]
    tipo = wo_tipo_meta(work_order.tipo)["label"]
    prioridad = dict(WORK_ORDER_PRIORITIES).get(work_order.prioridad, work_order.prioridad or "—")
    machine = work_order.machine
    currency = (getattr(empresa, "moneda", None) or "COP").upper()

    exporter.add_title(work_order.titulo or "Orden de Trabajo")
    exporter.add_kpis([
        ("Estado", status),
        ("Tipo", tipo),
        ("Prioridad", prioridad),
        ("Tiempo", work_order.tiempo_gastado_label or "—"),
    ])
    exporter.add_spacer()
    exporter.add_table(
        ["Dato", "Valor", "Dato", "Valor"],
        [
            ["Equipo", f"{machine.codigo} · {machine.nombre}" if machine else "—", "Área", work_order.area or getattr(machine, "area", "") or "—"],
            ["Ubicación", work_order.ubicacion or getattr(machine, "ubicacion", "") or "—", "Programada", _fecha(work_order.fecha_programada)],
            ["Inicio", _fecha(work_order.fecha_inicio, with_time=True), "Cierre", _fecha(work_order.fecha_cierre, with_time=True)],
            ["Ejecución", work_order.ejecucion_label, "Técnico", work_order.technician.nombre if work_order.technician else "—"],
        ],
    )
    exporter.add_spacer()
    exporter.add_title("Descripción y ejecución")
    exporter.add_paragraph(work_order.descripcion or "Sin observaciones registradas.")

    if work_order.es_ejecucion_externa:
        exporter.add_spacer()
        exporter.add_table(
            ["Proveedor", "Contacto", "Cotización", "Costos"],
            [[
                work_order.proveedor.nombre if work_order.proveedor else work_order.empresa_tercerizada or "—",
                work_order.contacto_proveedor or "—",
                work_order.numero_cotizacion or "—",
                f"Estimado: {_money(work_order.costo_estimado, currency)} · Real: {_money(work_order.costo_real, currency)}",
            ]],
        )

    if work_order.jornadas:
        exporter.add_spacer()
        exporter.add_title("Jornadas de trabajo")
        exporter.add_table(
            ["#", "Inicio", "Fin", "Técnico", "Avance"],
            [[j.orden, _fecha(j.fecha_inicio, with_time=True), _fecha(j.fecha_fin, with_time=True), j.tecnico_label, j.descripcion_avance or "—"] for j in work_order.jornadas],
        )

    if work_order.repuestos:
        exporter.add_spacer()
        exporter.add_titled_table(
            "Repuestos utilizados",
            ["SKU", "Repuesto", "Cantidad", "Costo unitario", "Total"],
            [[r.spare_part.sku if r.spare_part else "—", r.spare_part.nombre if r.spare_part else "—", r.cantidad, _money(r.costo_unitario_linea, currency), _money(r.costo_total_linea, currency)] for r in work_order.repuestos],
        )
    exporter.add_spacer(8)
    exporter.add_table(
        ["Autorizado por", "Recibido por", "Supervisor"],
        [[work_order.autorizado_por or "________________", work_order.recibido_por or "________________", work_order.supervisor.nombre if work_order.supervisor else "________________"]],
    )
    return exporter.save()
