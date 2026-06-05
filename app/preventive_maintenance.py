"""Planes y validación de mantenimiento preventivo por activo + actividad."""

from __future__ import annotations

import re
from calendar import monthrange
from datetime import date, timedelta
from typing import List, Optional, Tuple

from app import db
from app.models import (
    PreventiveMaintenancePlan,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderType,
    WORK_ORDER_TERMINAL_STATUSES,
)

PREVENTIVE_FREQUENCY_UNITS = (
    ("dias", "Días"),
    ("semanas", "Semanas"),
    ("meses", "Meses"),
)


def normalize_actividad(text: str) -> str:
    s = re.sub(r"\s+", " ", (text or "").strip().lower())
    return s


def actividad_key(text: str) -> str:
    return normalize_actividad(text)[:220]


def frecuencia_en_dias(valor: int, unidad: str) -> int:
    valor = max(1, int(valor or 1))
    unidad = (unidad or "meses").strip().lower()
    if unidad == "dias":
        return valor
    if unidad == "semanas":
        return valor * 7
    return valor * 30


def frecuencia_label(valor: Optional[int], unidad: Optional[str]) -> str:
    if not valor:
        return "—"
    unidad = (unidad or "meses").lower()
    labels = dict(PREVENTIVE_FREQUENCY_UNITS)
    return f"Cada {valor} {labels.get(unidad, unidad)}"


def preventive_wo_activa(
    machine_id: int, actividad: str, exclude_wo_id: Optional[int] = None
) -> Optional[WorkOrder]:
    key = actividad_key(actividad)
    if not key:
        return None
    plan = PreventiveMaintenancePlan.query.filter_by(
        machine_id=machine_id, actividad_key=key
    ).first()
    if not plan:
        return None
    q = WorkOrder.query.filter(
        WorkOrder.preventive_plan_id == plan.id,
        WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
        ~WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
    )
    if exclude_wo_id:
        q = q.filter(WorkOrder.id != exclude_wo_id)
    return q.first()


def get_or_create_plan(
    *,
    machine_id: int,
    empresa_id: Optional[int],
    actividad: str,
    frecuencia_valor: int,
    frecuencia_unidad: str,
) -> PreventiveMaintenancePlan:
    key = actividad_key(actividad)
    plan = PreventiveMaintenancePlan.query.filter_by(
        machine_id=machine_id, actividad_key=key
    ).first()
    if not plan:
        plan = PreventiveMaintenancePlan(
            empresa_id=empresa_id,
            machine_id=machine_id,
            actividad=actividad.strip(),
            actividad_key=key,
            frecuencia_valor=frecuencia_valor,
            frecuencia_unidad=frecuencia_unidad,
        )
        db.session.add(plan)
    else:
        plan.actividad = actividad.strip()
        plan.frecuencia_valor = frecuencia_valor
        plan.frecuencia_unidad = frecuencia_unidad
    return plan


def aplicar_preventivo_a_orden(
    wo: WorkOrder,
    actividad: str,
    frecuencia_valor: int,
    frecuencia_unidad: str,
    exclude_wo_id: Optional[int] = None,
) -> Optional[str]:
    """Vincula OT preventiva al plan; devuelve mensaje de error o None."""
    actividad = (actividad or "").strip()
    if not actividad:
        return "La actividad es obligatoria para mantenimiento preventivo."

    # Al editar una OT ya existente (p. ej. marcar completado) no se valida duplicado:
    # el calendario preventivo puede tener varias OT del mismo plan en el año.
    if exclude_wo_id is None:
        existente = preventive_wo_activa(wo.machine_id, actividad)
        if existente:
            num = existente.numero or f"#{existente.id}"
            return (
                f"Ya existe una OT preventiva activa para esta actividad en el equipo "
                f"({num}). Ciérrala antes de crear otra con la misma actividad."
            )

    unidad = (frecuencia_unidad or "meses").lower()
    if unidad not in {u for u, _ in PREVENTIVE_FREQUENCY_UNITS}:
        unidad = "meses"
    valor = max(1, int(frecuencia_valor or 1))

    plan = get_or_create_plan(
        machine_id=wo.machine_id,
        empresa_id=wo.empresa_id,
        actividad=actividad,
        frecuencia_valor=valor,
        frecuencia_unidad=unidad,
    )
    wo.titulo = plan.actividad
    wo.preventive_plan_id = plan.id
    wo.frecuencia_valor = valor
    wo.frecuencia_unidad = unidad
    return None


def parse_frecuencia_form(form) -> Tuple[int, str]:
    try:
        valor = int(form.get("frecuencia_valor") or 1)
    except ValueError:
        valor = 1
    unidad = (form.get("frecuencia_unidad") or "meses").strip().lower()
    return max(1, valor), unidad


def _add_frecuencia(fecha: date, valor: int, unidad: str) -> date:
    valor = max(1, int(valor or 1))
    unidad = (unidad or "meses").strip().lower()
    if unidad == "dias":
        return fecha + timedelta(days=valor)
    if unidad == "semanas":
        return fecha + timedelta(weeks=valor)
    mes = fecha.month + valor
    anio = fecha.year
    while mes > 12:
        mes -= 12
        anio += 1
    ultimo = monthrange(anio, mes)[1]
    return date(anio, mes, min(fecha.day, ultimo))


def fechas_preventivas_anio(
    fecha_inicio: date, valor: int, unidad: str, anio: Optional[int] = None
) -> List[date]:
    """Fechas programadas desde el ancla hasta fin de año según la frecuencia."""
    anio = anio or date.today().year
    fin_anio = date(anio, 12, 31)
    actual = fecha_inicio
    limite = 500
    while actual.year < anio and limite > 0:
        siguiente = _add_frecuencia(actual, valor, unidad)
        if siguiente <= actual:
            break
        actual = siguiente
        limite -= 1
    if actual.year > anio:
        return []

    fechas: List[date] = []
    while actual.year == anio and actual <= fin_anio and limite > 0:
        fechas.append(actual)
        siguiente = _add_frecuencia(actual, valor, unidad)
        if siguiente <= actual:
            break
        actual = siguiente
        limite -= 1
    return fechas


def _ot_preventiva_programada_existe(plan_id: int, fecha: date) -> bool:
    return (
        WorkOrder.query.filter(
            WorkOrder.preventive_plan_id == plan_id,
            WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
            WorkOrder.fecha_programada == fecha,
        ).first()
        is not None
    )


def crear_programacion_preventiva_anio(
    *,
    empresa_id: Optional[int],
    machine_id: int,
    technician_id: Optional[int],
    titulo: str,
    descripcion: str,
    prioridad: str,
    status: str,
    fecha_inicio: date,
    frecuencia_valor: int,
    frecuencia_unidad: str,
    ubicacion: str = "",
    area: str = "",
    autorizado_por: str = "",
    recibido_por: str = "",
    empresa_tercerizada: str = "",
) -> Tuple[List[WorkOrder], Optional[str]]:
    """
    Crea las OT preventivas del año en curso según la frecuencia indicada.
    Omite fechas que ya tengan OT en el mismo plan.
    """
    actividad = (titulo or "").strip()
    if not actividad:
        return [], "La actividad es obligatoria para mantenimiento preventivo."
    if not fecha_inicio:
        return [], "Indica la primera fecha programada para generar el calendario del año."

    unidad = (frecuencia_unidad or "meses").lower()
    if unidad not in {u for u, _ in PREVENTIVE_FREQUENCY_UNITS}:
        unidad = "meses"
    valor = max(1, int(frecuencia_valor or 1))

    anio = date.today().year
    fechas = fechas_preventivas_anio(fecha_inicio, valor, unidad, anio)
    if not fechas:
        return [], (
            f"No hay fechas de mantenimiento en {anio} con la primera fecha indicada "
            f"({fecha_inicio.strftime('%d/%m/%Y')})."
        )

    plan = get_or_create_plan(
        machine_id=machine_id,
        empresa_id=empresa_id,
        actividad=actividad,
        frecuencia_valor=valor,
        frecuencia_unidad=unidad,
    )

    ordenes: List[WorkOrder] = []
    for fecha_prog in fechas:
        if _ot_preventiva_programada_existe(plan.id, fecha_prog):
            continue
        wo = WorkOrder(
            empresa_id=empresa_id,
            titulo=plan.actividad,
            descripcion=(descripcion or "").strip(),
            tipo=WorkOrderType.PREVENTIVO.value,
            status=status or WorkOrderStatus.ABIERTA.value,
            prioridad=prioridad or "media",
            fecha_programada=fecha_prog,
            machine_id=machine_id,
            technician_id=technician_id,
            preventive_plan_id=plan.id,
            frecuencia_valor=valor,
            frecuencia_unidad=unidad,
            ubicacion=(ubicacion or "").strip(),
            area=(area or "").strip(),
            autorizado_por=(autorizado_por or "").strip(),
            recibido_por=(recibido_por or "").strip(),
            empresa_tercerizada=(empresa_tercerizada or "").strip(),
        )
        db.session.add(wo)
        ordenes.append(wo)

    if not ordenes:
        return [], (
            f"Ya existen OT preventivas para todas las fechas de {anio} "
            f"con esta actividad en el equipo."
        )
    return ordenes, None
