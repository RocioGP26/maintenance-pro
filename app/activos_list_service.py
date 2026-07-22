"""Datos enriquecidos para el listado de activos."""

from __future__ import annotations

from datetime import date
from typing import Any, Optional

from flask import url_for

from app.file_storage import url_for_reference

from app.models import (
    WORK_ORDER_TERMINAL_STATUSES,
    Machine,
    WorkOrder,
    WorkOrderStatus,
    machine_status_meta,
)

CRITICIDAD_NIVEL = {
    "baja": 1,
    "media": 2,
    "alta": 3,
    "critica": 3,
}

CRITICIDAD_LABEL = {
    "baja": "Baja",
    "media": "Media",
    "alta": "Alta",
    "critica": "Crítica",
}


def _machine_foto_url(machine: Machine) -> Optional[str]:
    url = (machine.foto_url or "").strip()
    if not url:
        return None
    return url_for_reference(url)


def _maintenance_por_maquina(machine_ids: list[int]) -> dict[int, dict[str, Optional[date]]]:
    vacio = {"ultimo": None, "proximo": None}
    if not machine_ids:
        return {}

    result = {mid: dict(vacio) for mid in machine_ids}
    hoy = date.today()
    abiertas = [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]

    completadas = (
        WorkOrder.query.filter(
            WorkOrder.machine_id.in_(machine_ids),
            WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
            WorkOrder.fecha_cierre.isnot(None),
        )
        .order_by(WorkOrder.fecha_cierre.desc(), WorkOrder.id.desc())
        .all()
    )
    for wo in completadas:
        mid = wo.machine_id
        if mid and result[mid]["ultimo"] is None and wo.fecha_cierre:
            result[mid]["ultimo"] = wo.fecha_cierre.date()

    proximas = (
        WorkOrder.query.filter(
            WorkOrder.machine_id.in_(machine_ids),
            WorkOrder.fecha_programada.isnot(None),
            WorkOrder.fecha_programada >= hoy,
            WorkOrder.status.in_(abiertas),
        )
        .order_by(WorkOrder.fecha_programada.asc(), WorkOrder.id.asc())
        .all()
    )
    for wo in proximas:
        mid = wo.machine_id
        if mid and result[mid]["proximo"] is None:
            result[mid]["proximo"] = wo.fecha_programada

    return result


def _fmt_fecha(d: Optional[date]) -> str:
    if not d:
        return "—"
    return d.strftime("%d/%m/%Y")


def machine_list_item(machine: Machine, maint: dict[str, Optional[date]]) -> dict[str, Any]:
    st = machine_status_meta(machine.status)
    crit_slug = (machine.criticidad or "media").strip().lower()
    nivel = CRITICIDAD_NIVEL.get(crit_slug, 2)
    search_blob = " ".join(
        filter(
            None,
            [
                machine.codigo,
                machine.nombre,
                machine.ubicacion,
                machine.area,
                machine.tipo_etiqueta,
            ],
        )
    ).lower()

    return {
        "id": machine.id,
        "codigo": machine.codigo,
        "nombre": machine.nombre,
        "tipo_id": machine.machine_type_id,
        "tipo_etiqueta": machine.tipo_etiqueta,
        "ubicacion": machine.ubicacion or "—",
        "area": machine.area or "",
        "status": machine.status,
        "status_slug": st["slug"],
        "status_label": st["label"],
        "criticidad": crit_slug,
        "criticidad_label": CRITICIDAD_LABEL.get(crit_slug, crit_slug.title()),
        "criticidad_nivel": nivel,
        "es_critico": bool(machine.es_critico),
        "foto_url": _machine_foto_url(machine),
        "ultimo_mant": _fmt_fecha(maint.get("ultimo")),
        "proximo_mant": _fmt_fecha(maint.get("proximo")),
        "ultimo_mant_iso": maint.get("ultimo").isoformat() if maint.get("ultimo") else "",
        "proximo_mant_iso": maint.get("proximo").isoformat() if maint.get("proximo") else "",
        "search_blob": search_blob,
        "href": url_for("main.activos_edit", id=machine.id),
        "delete_url": url_for("main.activos_delete", id=machine.id),
    }


def activos_kpis_from_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    operativos = sum(1 for i in items if i["status_slug"] == "operativo")
    mantenimiento = sum(1 for i in items if i["status_slug"] == "mantenimiento")
    falla = sum(1 for i in items if i["status_slug"] == "falla")
    criticos = sum(1 for i in items if i["es_critico"])

    def pct(n: int) -> int:
        return round(100 * n / total) if total else 0

    return {
        "total": total,
        "operativos": operativos,
        "mantenimiento": mantenimiento,
        "falla": falla,
        "criticos": criticos,
        "pct_operativos": pct(operativos),
        "pct_mantenimiento": pct(mantenimiento),
        "pct_falla": pct(falla),
    }


def build_activos_list_items(machines: list[Machine]) -> list[dict[str, Any]]:
    ids = [m.id for m in machines]
    maint_map = _maintenance_por_maquina(ids)
    return [machine_list_item(m, maint_map.get(m.id, {"ultimo": None, "proximo": None})) for m in machines]


def activos_kpis_for_machines(machines: list[Machine]) -> dict[str, Any]:
    return activos_kpis_from_items(build_activos_list_items(machines))
