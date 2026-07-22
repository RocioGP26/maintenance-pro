"""Reglas automáticas de estado para órdenes de trabajo."""

from __future__ import annotations

from datetime import date

from sqlalchemy import extract, exists, or_

from app import db
from app.models import (
    Machine,
    WorkOrder,
    WorkOrderJornada,
    WorkOrderStatus,
    WORK_ORDER_TERMINAL_STATUSES,
)

_ESTADOS_VENCEN = (
    WorkOrderStatus.ABIERTA.value,
    WorkOrderStatus.EN_PROCESO.value,
    WorkOrderStatus.PROGRAMADA.value,
)


def _filter_ordenes_empresa(q, empresa_id: int | None):
    if empresa_id is None:
        return q
    machine_ids = db.session.query(Machine.id).filter(Machine.empresa_id == empresa_id)
    return q.filter(
        or_(
            WorkOrder.empresa_id == empresa_id,
            WorkOrder.machine_id.in_(machine_ids),
        )
    )


def _solo_sin_jornadas(q):
    """OT con jornadas registradas: el estado lo define el avance, no la fecha programada."""
    tiene_jornadas = exists().where(WorkOrderJornada.work_order_id == WorkOrder.id)
    return q.filter(~tiene_jornadas)


def mismo_mes_programacion(fecha: date, hoy: date) -> bool:
    return fecha.year == hoy.year and fecha.month == hoy.month


def estado_inicial_por_fecha(fecha_programada: date | None, hoy: date | None = None) -> str:
    """
    Al crear o reprogramar sin jornadas:
    - Fuera del mes actual → Programada
    - En el mes actual (futura o hoy) → Abierta
    - Fecha pasada → Vencida
    """
    if not fecha_programada:
        return WorkOrderStatus.ABIERTA.value
    hoy = hoy or date.today()
    if fecha_programada < hoy:
        return WorkOrderStatus.VENCIDA.value
    if mismo_mes_programacion(fecha_programada, hoy):
        return WorkOrderStatus.ABIERTA.value
    return WorkOrderStatus.PROGRAMADA.value


def promover_programadas_abiertas(empresa_id: int | None = None, hoy: date | None = None) -> int:
    """Programada → Abierta cuando entra el mes de la fecha programada."""
    hoy = hoy or date.today()
    q = WorkOrder.query.filter(
        WorkOrder.status == WorkOrderStatus.PROGRAMADA.value,
        WorkOrder.fecha_programada.isnot(None),
        extract("year", WorkOrder.fecha_programada) == hoy.year,
        extract("month", WorkOrder.fecha_programada) == hoy.month,
        WorkOrder.fecha_programada >= hoy,
    )
    q = _solo_sin_jornadas(_filter_ordenes_empresa(q, empresa_id))
    n = q.update({WorkOrder.status: WorkOrderStatus.ABIERTA.value}, synchronize_session=False)
    if n:
        db.session.commit()
    return n


def reprogramar_abiertas_fuera_de_mes(empresa_id: int | None = None, hoy: date | None = None) -> int:
    """Abierta con fecha en otro mes (futuro) → Programada."""
    hoy = hoy or date.today()
    q = WorkOrder.query.filter(
        WorkOrder.status == WorkOrderStatus.ABIERTA.value,
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada >= hoy,
        or_(
            extract("year", WorkOrder.fecha_programada) != hoy.year,
            extract("month", WorkOrder.fecha_programada) != hoy.month,
        ),
    )
    q = _solo_sin_jornadas(_filter_ordenes_empresa(q, empresa_id))
    n = q.update({WorkOrder.status: WorkOrderStatus.PROGRAMADA.value}, synchronize_session=False)
    if n:
        db.session.commit()
    return n


def marcar_ordenes_vencidas(empresa_id: int | None = None, hoy: date | None = None) -> int:
    """OT no realizadas con fecha pasada → Vencida."""
    hoy = hoy or date.today()
    q = WorkOrder.query.filter(
        WorkOrder.status.in_(_ESTADOS_VENCEN),
        WorkOrder.fecha_programada.isnot(None),
        WorkOrder.fecha_programada < hoy,
    )
    q = _solo_sin_jornadas(_filter_ordenes_empresa(q, empresa_id))
    n = q.update({WorkOrder.status: WorkOrderStatus.VENCIDA.value}, synchronize_session=False)
    if n:
        db.session.commit()
    return n


def sincronizar_estados_ordenes(empresa_id: int | None = None, hoy: date | None = None) -> None:
    """Job ligero por request: vencidas, mes futuro y mes actual."""
    marcar_ordenes_vencidas(empresa_id, hoy)
    reprogramar_abiertas_fuera_de_mes(empresa_id, hoy)
    promover_programadas_abiertas(empresa_id, hoy)


def _es_terminal(status: str) -> bool:
    return (status or "").strip().lower() in WORK_ORDER_TERMINAL_STATUSES


def aplicar_estado_tras_jornadas(wo: WorkOrder, accion: str | None) -> None:
    """Tras registrar jornadas: En proceso, Abierta o Completada."""
    if _es_terminal(wo.status) or (wo.status or "").strip().lower() == WorkOrderStatus.CERRADA.value:
        return
    previous = wo.status
    key = (accion or "en_proceso").strip().lower()
    if key == "completado":
        wo.status = WorkOrderStatus.COMPLETADO.value
    elif key == "abierta":
        wo.status = WorkOrderStatus.ABIERTA.value
    else:
        wo.status = WorkOrderStatus.EN_PROCESO.value
    from app.integrations.emitters import emit_work_order_status_changed

    emit_work_order_status_changed(wo, previous_status=previous)


def resolver_estado_al_guardar(
    wo: WorkOrder,
    *,
    status_manual: str | None = None,
    jornada_estado_ot: str | None = None,
    tiene_jornadas: bool = False,
    hoy: date | None = None,
) -> None:
    """
    Prioridad al guardar:
    1. Cerrada (manual)
    2. Jornadas → Abierta / En proceso / Completada
    3. Completada manual
    4. Por fecha programada (sin jornadas o automático)
    """
    hoy = hoy or date.today()
    previous = wo.status
    manual = (status_manual or "").strip().lower()

    if manual == WorkOrderStatus.CERRADA.value:
        wo.status = WorkOrderStatus.CERRADA.value
        from app.integrations.emitters import emit_work_order_status_changed

        emit_work_order_status_changed(wo, previous_status=previous)
        return

    if _es_terminal(wo.status) and manual != WorkOrderStatus.COMPLETADO.value:
        return

    if tiene_jornadas:
        aplicar_estado_tras_jornadas(wo, jornada_estado_ot)
        return

    if manual == WorkOrderStatus.COMPLETADO.value:
        wo.status = WorkOrderStatus.COMPLETADO.value
        from app.integrations.emitters import emit_work_order_status_changed

        emit_work_order_status_changed(wo, previous_status=previous)
        return

    if manual == WorkOrderStatus.CERRADA.value:
        return

    wo.status = estado_inicial_por_fecha(wo.fecha_programada, hoy)
    from app.integrations.emitters import emit_work_order_status_changed

    emit_work_order_status_changed(wo, previous_status=previous)


def normalizar_estado_orden_por_fecha(wo: WorkOrder, hoy: date | None = None) -> None:
    """Compatibilidad: reprogramar sin jornadas."""
    if _es_terminal(wo.status) or (wo.status or "").strip().lower() == WorkOrderStatus.CERRADA.value:
        return
    if wo.jornadas and len(wo.jornadas) > 0:
        return
    resolver_estado_al_guardar(wo, tiene_jornadas=False, hoy=hoy)
