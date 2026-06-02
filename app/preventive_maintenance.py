"""Planes y validación de mantenimiento preventivo por activo + actividad."""

from __future__ import annotations

import re
from typing import Optional, Tuple

from app import db
from app.models import (
    PreventiveMaintenancePlan,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderType,
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
        WorkOrder.status != WorkOrderStatus.CERRADA.value,
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

    existente = preventive_wo_activa(wo.machine_id, actividad, exclude_wo_id=exclude_wo_id)
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
