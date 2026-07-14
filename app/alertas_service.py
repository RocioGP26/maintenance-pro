"""Resumen de alertas para la campana del header."""

from __future__ import annotations

from datetime import date
from typing import Any

from flask import request, url_for
from flask_login import current_user
from sqlalchemy import or_

from app import db
from app.models import Incident, InvVenta, Machine, WorkOrder, WorkOrderStatus


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


def _alertas_vacio() -> dict[str, Any]:
    return {
        "modulo": "",
        "titulo": "Alertas",
        "filas": [],
        "total": 0,
        "tiene_alertas": False,
    }


def _empacar_alertas(*, modulo: str, titulo: str, items: list[dict[str, Any]]) -> dict[str, Any]:
    total = sum(int(i.get("count") or 0) for i in items)
    return {
        "modulo": modulo,
        "titulo": titulo,
        "filas": items,
        "total": total,
        "tiene_alertas": total > 0,
    }


def _usar_alertas_inventario() -> bool:
    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO, modulos_activos_de

    empresa = getattr(current_user, "empresa", None) if current_user.is_authenticated else None
    mods = modulos_activos_de(empresa)
    if MODULO_INVENTARIO not in mods:
        return False
    if MODULO_MANTENIMIENTO not in mods:
        return True
    ep = (request.endpoint or "").strip()
    return ep.startswith("inv_comercial.")


def _resumen_alertas_mantenimiento(hoy: date) -> dict[str, Any]:
    from app.work_order_status import sincronizar_estados_ordenes

    sincronizar_estados_ordenes(_current_empresa_id(), hoy)
    base = _base_ordenes_empresa()

    vencimientos = aplicar_filtro_alerta_orden(base, "vencimientos", hoy).count()
    programados_hoy = aplicar_filtro_alerta_orden(base, "programados_hoy", hoy).count()
    en_proceso = aplicar_filtro_alerta_orden(base, "en_proceso", hoy).count()
    eid = _current_empresa_id()
    tickets_q = Incident.query.filter(Incident.resuelto.is_(False))
    if eid:
        tickets_q = tickets_q.filter(
            or_(
                Incident.empresa_id == eid,
                Incident.machine_id.in_(_machine_ids_for_empresa()),
            )
        )
    from app.permissions import is_read_only, is_requester

    if is_read_only(current_user) or is_requester(current_user):
        tickets_q = tickets_q.filter(Incident.user_id == current_user.id)
    tickets_pendientes = tickets_q.count()

    return _empacar_alertas(
        modulo="mantenimiento",
        titulo="Alertas críticas",
        items=[
            {
                "label": "Vencimientos",
                "count": vencimientos,
                "url": url_for("main.ordenes_list", alerta="vencimientos"),
                "tone": "danger",
            },
            {
                "label": "Programados hoy",
                "count": programados_hoy,
                "url": url_for("main.ordenes_list", alerta="programados_hoy"),
                "tone": "info",
                "pad": True,
            },
            {
                "label": "En proceso",
                "count": en_proceso,
                "url": url_for("main.ordenes_list", alerta="en_proceso"),
                "tone": "warn",
            },
            {
                "label": "Tickets pendientes",
                "count": tickets_pendientes,
                "url": url_for("main.incidencias_list", estado="pendiente"),
                "tone": "danger",
            },
        ],
    )


def _resumen_alertas_inventario(eid: int, hoy: date) -> dict[str, Any]:
    from app.inventario_comercial.service import alertas_cxp_compras, query_productos_bajo_stock

    bajo_stock = query_productos_bajo_stock(eid).count()
    por_cobrar = (
        InvVenta.query.filter_by(empresa_id=eid)
        .filter(InvVenta.estado_cobro.in_(["pendiente", "parcial"]))
        .count()
    )
    credito_vencido = (
        InvVenta.query.filter_by(empresa_id=eid)
        .filter(
            InvVenta.estado_cobro.in_(["pendiente", "parcial"]),
            InvVenta.fecha_vencimiento.isnot(None),
            InvVenta.fecha_vencimiento < hoy,
        )
        .count()
    )
    cxp = alertas_cxp_compras(eid, hoy)

    return _empacar_alertas(
        modulo="inventario",
        titulo="Alertas comerciales",
        items=[
            {
                "label": "Bajo stock",
                "count": bajo_stock,
                "url": url_for("inv_comercial.productos_list", alerta="bajo"),
                "tone": "danger",
            },
            {
                "label": "Facturas por vencer",
                "count": cxp["por_vencer_count"],
                "url": url_for("inv_comercial.cxp_list", alerta="por_vencer"),
                "tone": "warn",
            },
            {
                "label": "CxP vencidas",
                "count": cxp["vencidas_count"],
                "url": url_for("inv_comercial.cxp_list", alerta="vencidas"),
                "tone": "danger",
            },
            {
                "label": "Por cobrar",
                "count": por_cobrar,
                "url": url_for("inv_comercial.ventas_list", cobro="pendiente"),
                "tone": "warn",
            },
            {
                "label": "Crédito vencido",
                "count": credito_vencido,
                "url": url_for("inv_comercial.ventas_list", cobro="pendiente"),
                "tone": "danger",
            },
        ],
    )


def resumen_alertas_campana() -> dict[str, Any]:
    if not current_user.is_authenticated:
        return _alertas_vacio()

    hoy = date.today()
    if _usar_alertas_inventario():
        eid = _current_empresa_id()
        if not eid:
            return _alertas_vacio()
        return _resumen_alertas_inventario(eid, hoy)

    return _resumen_alertas_mantenimiento(hoy)
