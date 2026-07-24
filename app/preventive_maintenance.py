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


def ot_preventiva_misma_actividad(
    machine_id: int,
    actividad: str,
    *,
    fecha: Optional[date] = None,
    exclude_wo_id: Optional[int] = None,
) -> Optional[WorkOrder]:
    """OT preventiva existente: mismo equipo y misma actividad (opcionalmente misma fecha)."""
    key = actividad_key(actividad)
    if not key:
        return None
    q = WorkOrder.query.filter(
        WorkOrder.machine_id == machine_id,
        WorkOrder.tipo == WorkOrderType.PREVENTIVO.value,
        ~WorkOrder.status.in_(WORK_ORDER_TERMINAL_STATUSES),
    )
    if fecha is not None:
        q = q.filter(WorkOrder.fecha_programada == fecha)
    if exclude_wo_id:
        q = q.filter(WorkOrder.id != exclude_wo_id)
    for wo in q.all():
        if actividad_key(wo.titulo) == key:
            return wo
        if wo.preventive_plan_id:
            plan = db.session.get(PreventiveMaintenancePlan, wo.preventive_plan_id)
            if plan and plan.actividad_key == key:
                return wo
    return None


def validar_actividad_preventiva_nueva(
    machine_id: int, actividad: str, exclude_wo_id: Optional[int] = None
) -> Optional[str]:
    """Impide crear calendario/OT si ya hay preventivo activo con la misma actividad."""
    existente = ot_preventiva_misma_actividad(
        machine_id, actividad, exclude_wo_id=exclude_wo_id
    )
    if not existente:
        return None
    num = existente.numero or f"#{existente.id}"
    act = (existente.titulo or actividad).strip()
    return (
        f"Ya existe una OT preventiva «{act}» en este equipo ({num}). "
        "No se puede repetir la misma actividad hasta cerrar o completar la existente."
    )


def get_or_create_plan(
    *,
    machine_id: int,
    empresa_id: Optional[int],
    actividad: str,
    frecuencia_valor: int,
    frecuencia_unidad: str,
    tipo_codigo: str = "I",
) -> PreventiveMaintenancePlan:
    key = actividad_key(actividad)
    tipo = (tipo_codigo or "I").strip().upper()[:8] or "I"
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
            tipo_codigo=tipo,
        )
        db.session.add(plan)
    else:
        plan.actividad = actividad.strip()
        plan.frecuencia_valor = frecuencia_valor
        plan.frecuencia_unidad = frecuencia_unidad
        if tipo:
            plan.tipo_codigo = tipo
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
        err = validar_actividad_preventiva_nueva(wo.machine_id, actividad)
        if err:
            return err

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
    fecha_inicio: date,
    valor: int,
    unidad: str,
    anio: Optional[int] = None,
    *,
    desde: Optional[date] = None,
) -> List[date]:
    """Fechas programadas desde el ancla hasta fin de año según la frecuencia.

    ``desde`` (opcional) descarta fechas anteriores — p. ej. al generar OT a
    mitad de año solo se programan meses/semanas pendientes.
    """
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
        if desde is None or actual >= desde:
            fechas.append(actual)
        siguiente = _add_frecuencia(actual, valor, unidad)
        if siguiente <= actual:
            break
        actual = siguiente
        limite -= 1
    return fechas


def _ot_preventiva_programada_existe(
    machine_id: int, actividad: str, fecha: date, plan_id: Optional[int] = None
) -> bool:
    dup = ot_preventiva_misma_actividad(machine_id, actividad, fecha=fecha)
    if dup:
        return True
    if plan_id is None:
        return False
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
    fecha_inicio: date,
    frecuencia_valor: int,
    frecuencia_unidad: str,
    ubicacion: str = "",
    area: str = "",
    autorizado_por: str = "",
    recibido_por: str = "",
    empresa_tercerizada: str = "",
    omitir_validacion_actividad_abierta: bool = False,
    anio: Optional[int] = None,
    omitir_fechas_pasadas: bool = True,
) -> Tuple[List[WorkOrder], Optional[str]]:
    """
    Crea las OT preventivas del año según la frecuencia indicada.
    Omite fechas que ya tengan OT en el mismo plan.
    Por defecto no crea OT con fecha programada anterior a hoy (año en curso).
    """
    actividad = (titulo or "").strip()
    if not actividad:
        return [], "La actividad es obligatoria para mantenimiento preventivo."
    if not fecha_inicio:
        return [], "Indica la primera fecha programada para generar el calendario del año."

    if not omitir_validacion_actividad_abierta:
        err_dup = validar_actividad_preventiva_nueva(machine_id, actividad)
        if err_dup:
            return [], err_dup

    unidad = (frecuencia_unidad or "meses").lower()
    if unidad not in {u for u, _ in PREVENTIVE_FREQUENCY_UNITS}:
        unidad = "meses"
    valor = max(1, int(frecuencia_valor or 1))

    anio_obj = anio or date.today().year
    hoy = date.today()
    desde: Optional[date] = None
    if omitir_fechas_pasadas and anio_obj == hoy.year:
        desde = hoy
    elif omitir_fechas_pasadas and anio_obj < hoy.year:
        return [], (
            f"No se generan OT para {anio_obj}: el año ya concluyó. "
            "Selecciona el año en curso o uno futuro."
        )

    fechas = fechas_preventivas_anio(
        fecha_inicio, valor, unidad, anio_obj, desde=desde
    )
    if not fechas:
        if desde and anio_obj == hoy.year:
            return [], (
                f"No quedan mantenimientos pendientes en {anio_obj} "
                f"a partir de hoy ({hoy.strftime('%d/%m/%Y')}) con la frecuencia indicada."
            )
        return [], (
            f"No hay fechas de mantenimiento en {anio_obj} con la primera fecha indicada "
            f"({fecha_inicio.strftime('%d/%m/%Y')})."
        )

    plan = get_or_create_plan(
        machine_id=machine_id,
        empresa_id=empresa_id,
        actividad=actividad,
        frecuencia_valor=valor,
        frecuencia_unidad=unidad,
    )

    from app.work_order_status import estado_inicial_por_fecha

    ordenes: List[WorkOrder] = []
    for fecha_prog in fechas:
        if _ot_preventiva_programada_existe(machine_id, actividad, fecha_prog, plan.id):
            continue
        wo = WorkOrder(
            empresa_id=empresa_id,
            titulo=plan.actividad,
            descripcion=(descripcion or "").strip(),
            tipo=WorkOrderType.PREVENTIVO.value,
            status=estado_inicial_por_fecha(fecha_prog),
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
            f"Ya existen OT preventivas para todas las fechas pendientes de {anio_obj} "
            f"con esta actividad en el equipo."
        )
    return ordenes, None
