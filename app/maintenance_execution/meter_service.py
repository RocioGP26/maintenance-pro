"""Medidores y lecturas históricas por activo · Sprint 19.5."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app import db
from app.models import Machine, Technician, User, WorkOrder
from app.maintenance_execution.models import (
    AssetMeter,
    MeterEvent,
    MeterReading,
    METER_CUMULATIVE,
    METER_GAUGE,
)


MANAGER_ROLES = {"admin", "superadmin", "supervisor"}
ANOMALY_TYPES = {"reset", "replacement", "rollover", "sequence_adjustment", "out_of_range"}


def _role(user) -> str:
    return (getattr(user, "rol", "") or "").strip().lower()


def _manager(user) -> bool:
    return bool(getattr(user, "is_authenticated", False) and _role(user) in MANAGER_ROLES)


def _technician_for(user):
    return Technician.query.filter_by(
        empresa_id=getattr(user, "empresa_id", None), user_id=getattr(user, "id", None), activo=True
    ).first()


def technician_related_to_machine(user, machine: Machine) -> bool:
    if getattr(user, "empresa_id", None) != machine.empresa_id or _role(user) != "tecnico":
        return False
    if machine.responsable_user_id == user.id:
        return True
    technician = _technician_for(user)
    if technician is None:
        return False
    if machine.responsable_technician_id == technician.id:
        return True
    return WorkOrder.query.filter_by(
        empresa_id=machine.empresa_id, machine_id=machine.id, technician_id=technician.id
    ).first() is not None


def can_view_meters(user, machine: Machine) -> bool:
    if getattr(user, "empresa_id", None) != machine.empresa_id:
        return False
    return _manager(user) or technician_related_to_machine(user, machine)


def can_manage_meters(user, machine: Machine) -> bool:
    return getattr(user, "empresa_id", None) == machine.empresa_id and _manager(user)


def can_record_reading(user, meter: AssetMeter) -> bool:
    if getattr(user, "is_integration", False):
        return meter.active and getattr(user, "empresa_id", None) == meter.empresa_id
    return meter.active and can_view_meters(user, meter.machine)


def meters_for_machine(machine: Machine):
    return AssetMeter.query.filter_by(
        empresa_id=machine.empresa_id, machine_id=machine.id
    ).order_by(AssetMeter.active.desc(), AssetMeter.name.asc()).all()


def performers_for_meter(user, machine: Machine):
    if not _manager(user):
        return [user]
    return User.query.filter_by(empresa_id=machine.empresa_id, activo=True).filter(
        User.rol.in_(["tecnico", "supervisor", "admin", "superadmin"])
    ).order_by(User.nombre_visible, User.username).all()


def _code(value) -> str:
    result = re.sub(r"[^A-Z0-9_-]+", "_", (value or "").strip().upper()).strip("_")
    if not result or len(result) > 48:
        raise ValueError("El código del medidor es obligatorio y admite máximo 48 caracteres.")
    return result


def _rules(form) -> dict:
    result = {}
    for field, key in (("min_value", "min"), ("max_value", "max")):
        raw = (form.get(field) or "").strip()
        if raw:
            try:
                result[key] = float(Decimal(raw))
            except InvalidOperation as exc:
                raise ValueError("Los límites del medidor deben ser numéricos.") from exc
    if "min" in result and "max" in result and result["min"] > result["max"]:
        raise ValueError("El límite mínimo no puede superar el máximo.")
    return result


def create_meter(machine: Machine, actor, form) -> AssetMeter:
    if not can_manage_meters(actor, machine):
        raise ValueError("No tienes permiso para configurar medidores en este activo.")
    name = (form.get("name") or "").strip()
    unit = (form.get("unit") or "").strip()
    meter_type = (form.get("meter_type") or "").strip()
    if not name or len(name) > 120:
        raise ValueError("El nombre del medidor es obligatorio y admite máximo 120 caracteres.")
    if not unit or len(unit) > 24:
        raise ValueError("La unidad es obligatoria y admite máximo 24 caracteres.")
    if meter_type not in {METER_CUMULATIVE, METER_GAUGE}:
        raise ValueError("Selecciona un tipo de medidor válido.")
    try:
        decimals = int(form.get("decimals", 2))
    except (TypeError, ValueError) as exc:
        raise ValueError("Los decimales deben ser un número entre 0 y 6.") from exc
    if decimals < 0 or decimals > 6:
        raise ValueError("Los decimales deben estar entre 0 y 6.")
    code = _code(form.get("code"))
    if AssetMeter.query.filter_by(
        empresa_id=machine.empresa_id, machine_id=machine.id, code=code
    ).first():
        raise ValueError("Ya existe un medidor con ese código en el activo.")
    meter = AssetMeter(
        empresa_id=machine.empresa_id, machine_id=machine.id, code=code,
        name=name, meter_type=meter_type, unit=unit, decimals=decimals,
        rules_json=json.dumps(_rules(form), ensure_ascii=False), created_by_id=actor.id,
    )
    db.session.add(meter)
    db.session.flush()
    db.session.add(MeterEvent(
        empresa_id=meter.empresa_id, meter_id=meter.id, event="meter_created",
        actor_id=actor.id, detail=f"{meter.code} · {meter.name}",
    ))
    return meter


def set_meter_active(meter: AssetMeter, actor, active: bool):
    if not can_manage_meters(actor, meter.machine):
        raise ValueError("No tienes permiso para configurar este medidor.")
    meter.active = bool(active)
    db.session.add(MeterEvent(
        empresa_id=meter.empresa_id, meter_id=meter.id,
        event="meter_activated" if meter.active else "meter_deactivated",
        actor_id=actor.id, detail=meter.code,
    ))


def _decimal(value) -> Decimal:
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError("La lectura debe ser un valor numérico.") from exc
    if not result.is_finite():
        raise ValueError("La lectura debe ser un valor numérico finito.")
    return result


def _measured_at(value) -> datetime:
    raw = (value or "").strip()
    if not raw:
        return datetime.now().replace(second=0, microsecond=0)
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is not None:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError as exc:
        raise ValueError("La fecha y hora de lectura no son válidas.") from exc


def _performer(actor, machine: Machine, raw_id):
    if getattr(actor, "is_integration", False) and not raw_id:
        return actor
    if not _manager(actor):
        return actor
    performer_id = int(raw_id or actor.id)
    performer = User.query.filter_by(id=performer_id, empresa_id=machine.empresa_id, activo=True).first()
    if performer is None:
        raise ValueError("El ejecutor seleccionado no pertenece a la empresa activa.")
    return performer


def _sequence_anomaly(meter: AssetMeter, value: Decimal, measured_at: datetime) -> str:
    previous = MeterReading.query.filter(
        MeterReading.meter_id == meter.id, MeterReading.measured_at <= measured_at
    ).order_by(MeterReading.measured_at.desc(), MeterReading.id.desc()).first()
    following = MeterReading.query.filter(
        MeterReading.meter_id == meter.id, MeterReading.measured_at > measured_at
    ).order_by(MeterReading.measured_at.asc(), MeterReading.id.asc()).first()
    if previous is not None and value < Decimal(previous.value):
        return "regressive"
    if following is not None and value > Decimal(following.value):
        return "sequence"
    return ""


def record_reading(meter: AssetMeter, actor, form) -> MeterReading:
    if not can_record_reading(actor, meter):
        raise ValueError("No tienes permiso para registrar lecturas en este medidor.")
    value = _decimal(form.get("value"))
    if meter.meter_type == METER_CUMULATIVE and value < 0:
        raise ValueError("Un medidor acumulativo no admite lecturas negativas.")
    measured_at = _measured_at(form.get("measured_at"))
    performer = _performer(actor, meter.machine, form.get("performed_by_user_id"))
    justification = (form.get("justification") or "").strip()
    anomaly_type = (form.get("anomaly_type") or "").strip()
    flagged = False
    detected = ""
    if meter.meter_type == METER_CUMULATIVE:
        detected = _sequence_anomaly(meter, value, measured_at)
        if detected:
            if anomaly_type not in ANOMALY_TYPES - {"out_of_range"} or len(justification) < 5:
                raise ValueError("La lectura acumulativa altera la secuencia. Indica reinicio, reemplazo, rollover o ajuste y justifícalo.")
            flagged = True
    else:
        rules = meter.rules
        outside = ("min" in rules and value < Decimal(str(rules["min"]))) or (
            "max" in rules and value > Decimal(str(rules["max"])))
        if outside:
            if anomaly_type != "out_of_range" or len(justification) < 5:
                raise ValueError("La lectura está fuera del rango de referencia. Confirma la anomalía y agrega una justificación.")
            flagged = True
            detected = "out_of_range"
    correction = None
    correction_id = form.get("correction_of_id")
    if correction_id:
        correction = MeterReading.query.filter_by(
            id=int(correction_id), empresa_id=meter.empresa_id, meter_id=meter.id
        ).first()
        if correction is None:
            raise ValueError("La lectura que deseas corregir no pertenece a este medidor.")
        if len(justification) < 5:
            raise ValueError("La corrección requiere una justificación.")
    work_order = None
    work_order_id = form.get("work_order_id")
    if work_order_id:
        work_order = WorkOrder.query.filter_by(
            id=int(work_order_id), empresa_id=meter.empresa_id, machine_id=meter.machine_id
        ).first()
        if work_order is None:
            raise ValueError("La OT relacionada no pertenece a este activo.")
    reading = MeterReading(
        empresa_id=meter.empresa_id, meter_id=meter.id, work_order_id=work_order.id if work_order else None,
        value=value, measured_at=measured_at, source="correction" if correction else "manual",
        performed_by_user_id=performer.id, recorded_by_user_id=actor.id,
        notes=(form.get("notes") or "").strip()[:500], flagged=flagged,
        anomaly_type=anomaly_type if flagged else "", justification=justification[:500],
        correction_of_id=correction.id if correction else None,
    )
    db.session.add(reading)
    db.session.flush()
    event = "maintenance.meter.reading_flagged" if flagged else "maintenance.meter.reading_created"
    detail = f"{value} {meter.unit}"
    if detected:
        detail += f" · {detected} · {justification[:300]}"
    db.session.add(MeterEvent(
        empresa_id=meter.empresa_id, meter_id=meter.id, reading_id=reading.id,
        event=event, actor_id=actor.id, detail=detail[:500],
    ))
    from app.integrations.emitters import emit_meter_reading

    emit_meter_reading(reading, flagged=flagged)
    from app.maintenance_automation.service import evaluate_reading

    evaluate_reading(reading)
    from app.asset_health.service import save_health_snapshot

    save_health_snapshot(
        meter.machine, trigger="meter_reading", actor_id=actor.id
    )
    return reading


def seed_legacy_runtime_meters(empresa_id: int | None = None) -> int:
    """Crea el horómetro y lectura inicial de horas_operacion sin duplicados."""
    query = Machine.query.filter(Machine.horas_operacion.isnot(None))
    if empresa_id is not None:
        query = query.filter(Machine.empresa_id == empresa_id)
    created = 0
    for machine in query.all():
        if machine.empresa_id is None:
            continue
        meter = AssetMeter.query.filter_by(
            empresa_id=machine.empresa_id, machine_id=machine.id, code="RUNTIME_HOURS"
        ).first()
        if meter is None:
            meter = AssetMeter(
                empresa_id=machine.empresa_id, machine_id=machine.id, code="RUNTIME_HOURS",
                name="Horómetro", meter_type=METER_CUMULATIVE, unit="h", decimals=2,
                rules_json="{}", created_by_id=None,
            )
            db.session.add(meter); db.session.flush()
            db.session.add(MeterEvent(
                empresa_id=machine.empresa_id, meter_id=meter.id,
                event="meter_created_from_legacy", actor_id=None, detail="Machine.horas_operacion",
            ))
        key = f"legacy-runtime-hours-machine-{machine.id}"
        exists = MeterReading.query.filter_by(empresa_id=machine.empresa_id, idempotency_key=key).first()
        if exists is None:
            reading = MeterReading(
                empresa_id=machine.empresa_id, meter_id=meter.id, value=Decimal(str(machine.horas_operacion)),
                measured_at=datetime.utcnow(), source="legacy_migration", idempotency_key=key,
                notes="Lectura inicial importada desde Machine.horas_operacion.",
            )
            db.session.add(reading); db.session.flush()
            db.session.add(MeterEvent(
                empresa_id=machine.empresa_id, meter_id=meter.id, reading_id=reading.id,
                event="maintenance.meter.reading_created", actor_id=None, detail="legacy_migration",
            ))
            created += 1
    return created
