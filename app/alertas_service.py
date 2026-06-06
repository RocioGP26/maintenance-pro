"""Resumen de alertas para la campana del header."""

from __future__ import annotations

from datetime import date
from typing import Any

from flask import url_for
from flask_login import current_user
from sqlalchemy import or_

from app import db
from app.models import Machine, WorkOrder, WorkOrderStatus


def _current_empresa_id() -> int | None:
    from app.tenancy.context import current_empresa_id

    return current_empresa_id()


def _machine_ids_for_empresa():
    q = db.session.query(Machine.id)
    eid = _current_empresa_id()
    if eid:
        q = q.filter(Machine.empresa_id == eid)
    return q


def _filter_work_orders_empresa(q):
    eid = _current_empresa_id()
    if not eid:
        return q
    return q.filter(
        or_(
            WorkOrder.empresa_id == eid,
            WorkOrder.machine_id.in_(_machine_ids_for_empresa()),
        )
    )


OT_ALERT_ABIERTAS = (WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value)


def _base_ordenes_empresa():
    return _filter_work_orders_empresa(WorkOrder.query)


def aplicar_filtro_alerta_orden(q, alerta: str, hoy: date | None = None):
    """Misma lógica que la campana del header → lista de OT."""
    hoy = hoy or date.today()
    key = (alerta or "").strip().lower()
    if key == "vencimientos":
        return q.filter(WorkOrder.status == WorkOrderStatus.VENCIDA.value)
    if key == "programados_hoy":
        return q.filter(
            WorkOrder.fecha_programada == hoy,
            WorkOrder.status.in_(OT_ALERT_ABIERTAS),
        )
    if key == "en_proceso":
        return q.filter(WorkOrder.status == WorkOrderStatus.EN_PROCESO.value)
    return q


def resumen_alertas_campana() -> dict[str, Any]:
    vacio: dict[str, Any] = {
        "vencimientos": 0,
        "programados_hoy": 0,
        "en_proceso": 0,
        "total": 0,
        "tiene_alertas": False,
        "url_vencimientos": "",
        "url_programados_hoy": "",
        "url_en_proceso": "",
    }
    if not current_user.is_authenticated:
        return vacio

    hoy = date.today()
    from app.work_order_status import sincronizar_estados_ordenes

    sincronizar_estados_ordenes(_current_empresa_id(), hoy)
    base = _base_ordenes_empresa()

    vencimientos = aplicar_filtro_alerta_orden(base, "vencimientos", hoy).count()
    programados_hoy = aplicar_filtro_alerta_orden(base, "programados_hoy", hoy).count()
    en_proceso = aplicar_filtro_alerta_orden(base, "en_proceso", hoy).count()
    total = vencimientos + programados_hoy + en_proceso

    return {
        "vencimientos": vencimientos,
        "programados_hoy": programados_hoy,
        "en_proceso": en_proceso,
        "total": total,
        "tiene_alertas": total > 0,
        "url_vencimientos": url_for("main.ordenes_list", alerta="vencimientos"),
        "url_programados_hoy": url_for("main.ordenes_list", alerta="programados_hoy"),
        "url_en_proceso": url_for("main.ordenes_list", alerta="en_proceso"),
    }
