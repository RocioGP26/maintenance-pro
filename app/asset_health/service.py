"""Motor determinista y explicable de salud de activos."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import or_

from app import db
from app.asset_health.models import AssetHealthSnapshot
from app.maintenance_execution.models import AssetMeter, MeterReading, METER_GAUGE
from app.models import (
    Incident,
    IncidentEstado,
    Machine,
    MachineStatus,
    WorkOrder,
    WorkOrderStatus,
    WorkOrderType,
)


BAND_META = {
    "healthy": {"label": "Saludable", "tone": "success"},
    "watch": {"label": "En observación", "tone": "info"},
    "at_risk": {"label": "En riesgo", "tone": "warning"},
    "critical": {"label": "Crítico", "tone": "danger"},
    "unknown": {"label": "Sin datos", "tone": "secondary"},
}
FACTOR_WEIGHTS = {"operational": 30, "maintenance": 25, "reliability": 20, "condition": 25}
OPEN_INCIDENT_STATES = tuple(
    state.value for state in IncidentEstado
    if state not in {IncidentEstado.RESUELTO, IncidentEstado.CERRADO, IncidentEstado.CANCELADO}
)


def health_band(score: int, confidence: int) -> str:
    if confidence < 30:
        return "unknown"
    if score >= 85:
        return "healthy"
    if score >= 70:
        return "watch"
    if score >= 50:
        return "at_risk"
    return "critical"


def _factor(key: str, label: str, score: int, observed: bool, evidence: str) -> dict:
    return {
        "key": key,
        "label": label,
        "score": max(0, min(100, int(round(score)))),
        "weight": FACTOR_WEIGHTS[key],
        "observed": bool(observed),
        "evidence": evidence,
    }


def _operational_factor(machine: Machine) -> dict:
    status = (machine.status or "").strip().lower()
    score = {
        MachineStatus.OPERATIVO.value: 100,
        MachineStatus.MANTENIMIENTO.value: 45,
        MachineStatus.FALLA.value: 0,
    }.get(status, 50)
    label = {"operativo": "operativo", "mantenimiento": "en mantenimiento", "falla": "en falla"}.get(status, status or "sin estado")
    return _factor("operational", "Estado operativo", score, bool(status), f"Activo {label}.")


def _maintenance_factor(machine: Machine, as_of: date) -> tuple[dict, list[str]]:
    orders = WorkOrder.query.filter_by(empresa_id=machine.empresa_id, machine_id=machine.id)
    overdue = orders.filter(WorkOrder.status == WorkOrderStatus.VENCIDA.value).count()
    open_count = orders.filter(WorkOrder.status.in_((
        WorkOrderStatus.ABIERTA.value, WorkOrderStatus.EN_PROCESO.value,
        WorkOrderStatus.PROGRAMADA.value,
    ))).count()
    pending_close = orders.filter(WorkOrder.status == WorkOrderStatus.COMPLETADO.value).count()
    score = max(0, 100 - overdue * 25 - open_count * 8 - pending_close * 10)
    reasons = []
    if overdue:
        reasons.append(f"{overdue} OT vencida(s)")
    if pending_close:
        reasons.append(f"{pending_close} OT pendiente(s) de cierre")
    evidence = f"{overdue} vencidas · {open_count} abiertas/programadas · {pending_close} pendientes de cierre"
    return _factor("maintenance", "Mantenimiento", score, True, evidence), reasons


def _reliability_factor(machine: Machine, as_of: date) -> tuple[dict, list[str]]:
    since = as_of - timedelta(days=90)
    correctives = WorkOrder.query.filter(
        WorkOrder.empresa_id == machine.empresa_id,
        WorkOrder.machine_id == machine.id,
        WorkOrder.tipo == WorkOrderType.CORRECTIVO.value,
        or_(WorkOrder.fecha_programada >= since, WorkOrder.created_at >= datetime.combine(since, datetime.min.time())),
    ).count()
    incidents = Incident.query.filter(
        Incident.empresa_id == machine.empresa_id,
        Incident.machine_id == machine.id,
        Incident.estado.in_(OPEN_INCIDENT_STATES),
    ).count()
    score = max(0, 100 - min(60, correctives * 15) - min(40, incidents * 15))
    reasons = []
    if correctives >= 2:
        reasons.append(f"{correctives} correctivos en 90 días")
    if incidents:
        reasons.append(f"{incidents} incidencia(s) abierta(s)")
    evidence = f"{correctives} correctivos/90 días · {incidents} incidencias abiertas"
    return _factor("reliability", "Confiabilidad", score, True, evidence), reasons


def _condition_factor(machine: Machine, as_of: date) -> tuple[dict, list[str]]:
    meters = AssetMeter.query.filter_by(
        empresa_id=machine.empresa_id, machine_id=machine.id, active=True
    ).all()
    scores, details, reasons = [], [], []
    cutoff = datetime.combine(as_of - timedelta(days=30), datetime.min.time())
    for meter in meters:
        latest = MeterReading.query.filter_by(meter_id=meter.id).order_by(
            MeterReading.measured_at.desc(), MeterReading.id.desc()
        ).first()
        rules = meter.rules
        assessable = meter.meter_type == METER_GAUGE and ("min" in rules or "max" in rules)
        if not assessable and not (latest and latest.flagged):
            continue
        if latest is None:
            scores.append(40)
            details.append(f"{meter.name}: sin lectura")
            reasons.append(f"{meter.name} sin lectura")
            continue
        value = Decimal(latest.value)
        outside = latest.flagged or (
            "min" in rules and value < Decimal(str(rules["min"]))
        ) or ("max" in rules and value > Decimal(str(rules["max"])))
        if outside:
            scores.append(0)
            details.append(f"{meter.name}: fuera de rango")
            reasons.append(f"{meter.name} fuera de rango")
        elif latest.measured_at < cutoff:
            scores.append(60)
            details.append(f"{meter.name}: lectura desactualizada")
            reasons.append(f"{meter.name} sin lectura reciente")
        else:
            scores.append(100)
            details.append(f"{meter.name}: dentro de rango")
    if not scores:
        return _factor(
            "condition", "Condición medida", 50, False,
            "Sin medidores evaluables; se aplica valor neutral y baja la confianza.",
        ), ["Configura medidores con rangos para aumentar la confianza"]
    return _factor(
        "condition", "Condición medida", round(sum(scores) / len(scores)), True,
        " · ".join(details[:5]),
    ), reasons


def calculate_asset_health(machine: Machine, as_of: date | None = None) -> dict:
    as_of = as_of or date.today()
    operational = _operational_factor(machine)
    maintenance, maintenance_reasons = _maintenance_factor(machine, as_of)
    reliability, reliability_reasons = _reliability_factor(machine, as_of)
    condition, condition_reasons = _condition_factor(machine, as_of)
    factors = [operational, maintenance, reliability, condition]
    score = round(sum(item["score"] * item["weight"] for item in factors) / 100)
    confidence = sum(item["weight"] for item in factors if item["observed"])
    reasons = maintenance_reasons + reliability_reasons + condition_reasons
    if machine.es_critico and score < 70:
        reasons.insert(0, "Activo crítico con salud inferior a 70")
    band = health_band(score, confidence)
    return {
        "machine": machine,
        "score": score,
        "confidence": confidence,
        "band": band,
        "band_label": BAND_META[band]["label"],
        "tone": BAND_META[band]["tone"],
        "factors": factors,
        "reasons": reasons,
        "calculated_on": as_of,
    }


def save_health_snapshot(machine: Machine, *, trigger: str, actor_id: int | None = None) -> AssetHealthSnapshot:
    result = calculate_asset_health(machine)
    latest = AssetHealthSnapshot.query.filter_by(
        empresa_id=machine.empresa_id, machine_id=machine.id
    ).order_by(AssetHealthSnapshot.calculated_at.desc()).first()
    previous_band = latest.band if latest else None
    factors_json = json.dumps(result["factors"], ensure_ascii=False, sort_keys=True)
    reasons_json = json.dumps(result["reasons"], ensure_ascii=False)
    if latest and latest.score == result["score"] and latest.confidence == result["confidence"] and latest.band == result["band"] and latest.factors_json == factors_json and latest.reasons_json == reasons_json:
        return latest
    snapshot = AssetHealthSnapshot(
        empresa_id=machine.empresa_id, machine_id=machine.id,
        score=result["score"], confidence=result["confidence"], band=result["band"],
        factors_json=factors_json, reasons_json=reasons_json,
        trigger=(trigger or "manual")[:48], actor_id=actor_id,
    )
    db.session.add(snapshot)
    db.session.flush()
    if previous_band != snapshot.band:
        from app.integrations.emitters import emit_asset_health_band_changed

        emit_asset_health_band_changed(snapshot, previous_band=previous_band)
    return snapshot


def portfolio_health(machines: list[Machine]) -> dict:
    items = [calculate_asset_health(machine) for machine in machines]
    counts = {key: 0 for key in BAND_META}
    for item in items:
        counts[item["band"]] += 1
    average = round(sum(item["score"] for item in items) / len(items)) if items else None
    confidence = round(sum(item["confidence"] for item in items) / len(items)) if items else None
    return {"items": items, "counts": counts, "average": average, "confidence": confidence, "total": len(items)}


def refresh_tenant_health(empresa_id: int, *, trigger: str = "manual", actor_id: int | None = None) -> int:
    machines = Machine.query.filter_by(empresa_id=empresa_id).all()
    before = db.session.query(AssetHealthSnapshot.id).filter_by(empresa_id=empresa_id).count()
    for machine in machines:
        save_health_snapshot(machine, trigger=trigger, actor_id=actor_id)
    db.session.flush()
    after = db.session.query(AssetHealthSnapshot.id).filter_by(empresa_id=empresa_id).count()
    return after - before


def latest_attention_count(user) -> int:
    """Cuenta el último snapshot en riesgo/crítico dentro del alcance del usuario."""
    empresa_id = getattr(user, "empresa_id", None)
    if not empresa_id:
        return 0
    latest_ids = db.session.query(
        db.func.max(AssetHealthSnapshot.id).label("snapshot_id")
    ).filter(AssetHealthSnapshot.empresa_id == empresa_id).group_by(
        AssetHealthSnapshot.machine_id
    ).subquery()
    query = AssetHealthSnapshot.query.join(
        latest_ids, AssetHealthSnapshot.id == latest_ids.c.snapshot_id
    ).filter(AssetHealthSnapshot.band.in_(("at_risk", "critical")))
    if (getattr(user, "rol", "") or "").strip().lower() == "tecnico":
        from app.models import Technician

        technician = Technician.query.filter_by(
            empresa_id=empresa_id, user_id=user.id, activo=True
        ).first()
        assigned = db.session.query(WorkOrder.machine_id).filter(
            WorkOrder.empresa_id == empresa_id,
            WorkOrder.technician_id == (technician.id if technician else -1),
        )
        machine_ids = db.session.query(Machine.id).filter(
            Machine.empresa_id == empresa_id,
            or_(
                Machine.responsable_user_id == user.id,
                Machine.responsable_technician_id == (technician.id if technician else -1),
                Machine.id.in_(assigned),
            ),
        )
        query = query.filter(AssetHealthSnapshot.machine_id.in_(machine_ids))
    return query.count()
