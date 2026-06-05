"""Resumen de alertas para la campana del header."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from flask import url_for
from flask_login import current_user
from sqlalchemy import or_

from app import db
from app.models import Machine, WorkOrder, WorkOrderStatus


def _current_empresa_id() -> int | None:
    if not current_user.is_authenticated:
        return None
    return current_user.empresa_id


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
    ayer = hoy - timedelta(days=1)
    abiertas = [WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value]
    base = _filter_work_orders_empresa(WorkOrder.query)

    vencimientos = base.filter(
        WorkOrder.status.in_(abiertas),
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada < hoy,
    ).count()

    programados_hoy = base.filter(
        WorkOrder.fecha_programada == hoy,
        WorkOrder.status.in_(abiertas),
    ).count()

    en_proceso = base.filter(WorkOrder.status == WorkOrderStatus.EN_PROCESO.value).count()
    total = vencimientos + programados_hoy + en_proceso

    return {
        "vencimientos": vencimientos,
        "programados_hoy": programados_hoy,
        "en_proceso": en_proceso,
        "total": total,
        "tiene_alertas": total > 0,
        "url_vencimientos": url_for("main.ordenes_list", fecha_hasta=ayer.isoformat()),
        "url_programados_hoy": url_for(
            "main.ordenes_list",
            fecha_desde=hoy.isoformat(),
            fecha_hasta=hoy.isoformat(),
        ),
        "url_en_proceso": url_for("main.ordenes_list", status=WorkOrderStatus.EN_PROCESO.value),
    }
