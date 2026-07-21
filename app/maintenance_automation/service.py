"""Motor síncrono, determinista e idempotente de automatizaciones."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from sqlalchemy import and_, or_

from app import db
from app.maintenance_automation.models import (
    MaintenanceAutomationEvent,
    MaintenanceAutomationExecution,
    MaintenanceAutomationNotification,
    MaintenanceAutomationRule,
)
from app.maintenance_execution.models import AssetMeter, MeterReading
from app.models import Technician, User, WorkOrder, WorkOrderStatus, WorkOrderType
from app.wo_numbering import asignar_numero_ot
from app.work_order_status import estado_inicial_por_fecha


MANAGER_ROLES = {"admin", "superadmin", "supervisor"}
OPERATORS = {"gt": ">", "gte": "≥", "lt": "<", "lte": "≤"}
ACTION_TYPES = {"notify", "create_work_order"}
WORK_ORDER_TYPES = {
    WorkOrderType.CORRECTIVO.value,
    WorkOrderType.PREVENTIVO.value,
    WorkOrderType.EMERGENCIA.value,
}
PRIORITIES = {"baja", "media", "alta", "critica"}


def can_manage_automations(user) -> bool:
    return bool(
        getattr(user, "is_authenticated", False)
        and (getattr(user, "rol", "") or "").strip().lower() in MANAGER_ROLES
    )


def rules_for_tenant(empresa_id: int):
    return MaintenanceAutomationRule.query.filter_by(empresa_id=empresa_id).order_by(
        MaintenanceAutomationRule.active.desc(), MaintenanceAutomationRule.name.asc()
    ).all()


def unread_automation_notifications(user):
    if not getattr(user, "is_authenticated", False) or not getattr(user, "empresa_id", None):
        return []
    return MaintenanceAutomationNotification.query.filter_by(
        empresa_id=user.empresa_id, user_id=user.id, read_at=None
    ).order_by(MaintenanceAutomationNotification.created_at.desc()).all()


def mark_automation_notification_read(item, user):
    if item.empresa_id != user.empresa_id or item.user_id != user.id:
        raise ValueError("La notificación no pertenece al usuario autenticado.")
    if item.read_at is None:
        item.read_at = datetime.utcnow()


def _decimal(value, label="El umbral") -> Decimal:
    try:
        result = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"{label} debe ser numérico.") from exc
    if not result.is_finite():
        raise ValueError(f"{label} debe ser finito.")
    return result


def _action_config(empresa_id: int, action_type: str, form) -> dict:
    raw_roles = form.getlist("notify_roles") if hasattr(form, "getlist") else form.get("notify_roles", [])
    if isinstance(raw_roles, str):
        raw_roles = [raw_roles]
    roles = [role for role in raw_roles if role in {"admin", "supervisor"}]
    if not roles:
        roles = ["admin", "supervisor"]
    config = {"notify_roles": roles}
    if action_type == "create_work_order":
        wo_type = (form.get("work_order_type") or "correctivo").strip().lower()
        priority = (form.get("priority") or "media").strip().lower()
        if wo_type not in WORK_ORDER_TYPES:
            raise ValueError("Selecciona un tipo de OT válido.")
        if priority not in PRIORITIES:
            raise ValueError("Selecciona una prioridad válida.")
        title = (form.get("work_order_title") or "").strip()
        if not title or len(title) > 200:
            raise ValueError("El título de la OT es obligatorio y admite máximo 200 caracteres.")
        try:
            technician_id = int(form.get("technician_id")) if form.get("technician_id") else None
        except (TypeError, ValueError) as exc:
            raise ValueError("Selecciona un técnico válido.") from exc
        if technician_id:
            technician = Technician.query.filter_by(
                id=technician_id, empresa_id=empresa_id, activo=True
            ).first()
            if technician is None:
                raise ValueError("El técnico de la acción no pertenece a la empresa activa.")
        config.update({
            "work_order_type": wo_type,
            "priority": priority,
            "title": title,
            "description": (form.get("work_order_description") or "").strip()[:1000],
            "technician_id": technician_id,
        })
    return config


def create_rule(empresa_id: int, actor, form) -> MaintenanceAutomationRule:
    if actor.empresa_id != empresa_id or not can_manage_automations(actor):
        raise ValueError("No tienes permiso para administrar automatizaciones.")
    name = (form.get("name") or "").strip()
    if not name or len(name) > 160:
        raise ValueError("El nombre es obligatorio y admite máximo 160 caracteres.")
    if MaintenanceAutomationRule.query.filter_by(empresa_id=empresa_id, name=name).first():
        raise ValueError("Ya existe una automatización con ese nombre.")
    try:
        meter_id = int(form.get("meter_id"))
    except (TypeError, ValueError) as exc:
        raise ValueError("Selecciona un medidor activo de la empresa.") from exc
    meter = AssetMeter.query.filter_by(id=meter_id, empresa_id=empresa_id, active=True).first()
    if meter is None:
        raise ValueError("Selecciona un medidor activo de la empresa.")
    operator = (form.get("operator") or "").strip()
    if operator not in OPERATORS:
        raise ValueError("Selecciona un operador válido.")
    threshold = _decimal(form.get("threshold"))
    action_type = (form.get("action_type") or "").strip()
    if action_type not in ACTION_TYPES:
        raise ValueError("Selecciona una acción válida.")
    try:
        cooldown = int(form.get("cooldown_minutes") or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError("El tiempo de enfriamiento debe expresarse en minutos.") from exc
    if cooldown < 0 or cooldown > 525600:
        raise ValueError("El enfriamiento debe estar entre 0 y 525600 minutos.")
    rule = MaintenanceAutomationRule(
        empresa_id=empresa_id, name=name,
        description=(form.get("description") or "").strip()[:500],
        meter_id=meter.id, operator=operator, threshold=threshold,
        crossing_only=form.get("crossing_only") == "1", cooldown_minutes=cooldown,
        action_type=action_type,
        action_json=json.dumps(_action_config(empresa_id, action_type, form), ensure_ascii=False),
        created_by_id=actor.id,
    )
    db.session.add(rule); db.session.flush()
    db.session.add(MaintenanceAutomationEvent(
        empresa_id=empresa_id, rule_id=rule.id, event="automation_rule_created",
        actor_id=actor.id, detail=f"{meter.code} {OPERATORS[operator]} {threshold}",
    ))
    return rule


def set_rule_active(rule: MaintenanceAutomationRule, actor, active: bool):
    if actor.empresa_id != rule.empresa_id or not can_manage_automations(actor):
        raise ValueError("No tienes permiso para modificar esta automatización.")
    rule.active = bool(active)
    db.session.add(MaintenanceAutomationEvent(
        empresa_id=rule.empresa_id, rule_id=rule.id,
        event="automation_rule_activated" if active else "automation_rule_deactivated",
        actor_id=actor.id, detail=rule.name,
    ))


def _matches(value: Decimal, operator: str, threshold: Decimal) -> bool:
    return {
        "gt": value > threshold,
        "gte": value >= threshold,
        "lt": value < threshold,
        "lte": value <= threshold,
    }[operator]


def _previous_reading(reading: MeterReading):
    return MeterReading.query.filter(
        MeterReading.meter_id == reading.meter_id,
        MeterReading.id != reading.id,
        or_(
            MeterReading.measured_at < reading.measured_at,
            and_(MeterReading.measured_at == reading.measured_at, MeterReading.id < reading.id),
        ),
    ).order_by(MeterReading.measured_at.desc(), MeterReading.id.desc()).first()


def _execution(rule, reading, *, status, matched, reason="", error=""):
    item = MaintenanceAutomationExecution(
        empresa_id=rule.empresa_id, rule_id=rule.id, reading_id=reading.id,
        status=status, matched=matched, reason=reason,
        condition_snapshot=f"{reading.value} {rule.meter.unit} {OPERATORS[rule.operator]} {rule.threshold}",
        action_snapshot=rule.action_json[:500], error=error[:500],
    )
    db.session.add(item); db.session.flush()
    return item


def _recipients(rule, config, technician=None):
    roles = config.get("notify_roles") or ["admin", "supervisor"]
    users = User.query.filter(
        User.empresa_id == rule.empresa_id, User.activo.is_(True), User.bloqueado.is_(False),
        User.rol.in_(roles),
    ).all()
    if technician and technician.user and technician.user.activo and not technician.user.bloqueado:
        users.append(technician.user)
    unique = {}
    for user in users:
        unique[user.id] = user
    return list(unique.values())


def _notify(execution, users, title, message):
    for user in users:
        db.session.add(MaintenanceAutomationNotification(
            empresa_id=execution.empresa_id, execution_id=execution.id, user_id=user.id,
            title=title[:180], message=message[:500],
        ))


def _perform_action(rule, reading, execution):
    config = json.loads(rule.action_json or "{}")
    meter = rule.meter
    message = (
        f"{meter.machine.codigo} · {meter.name}: {reading.value} {meter.unit} "
        f"cumplió {OPERATORS[rule.operator]} {rule.threshold}."
    )
    if rule.action_type == "notify":
        _notify(execution, _recipients(rule, config), f"Automatización: {rule.name}", message)
        execution.action_snapshot = "Aviso interno creado"
        return
    technician = None
    if config.get("technician_id"):
        technician = Technician.query.filter_by(
            id=config["technician_id"], empresa_id=rule.empresa_id, activo=True
        ).first()
    wo = WorkOrder(
        empresa_id=rule.empresa_id, machine_id=meter.machine_id,
        titulo=config["title"],
        descripcion=(config.get("description") or "") + (
            f"\n\n[Automatización {rule.name}: lectura {reading.value} {meter.unit}; "
            f"umbral {OPERATORS[rule.operator]} {rule.threshold}]"
        ),
        tipo=config.get("work_order_type", "correctivo"),
        prioridad=config.get("priority", "media"),
        technician_id=technician.id if technician else None,
        fecha_programada=date.today(), status=estado_inicial_por_fecha(date.today()),
        ubicacion=meter.machine.ubicacion or "", area=meter.machine.area or "",
    )
    db.session.add(wo); db.session.flush(); asignar_numero_ot(wo)
    from app.asset_health.service import save_health_snapshot

    save_health_snapshot(
        meter.machine,
        trigger="automation_work_order",
        actor_id=reading.recorded_by_user_id,
    )
    execution.work_order_id = wo.id
    execution.action_snapshot = f"OT {wo.numero} creada"
    _notify(
        execution, _recipients(rule, config, technician),
        f"OT automática {wo.numero}", f"{message} Se creó {wo.numero}: {wo.titulo}.",
    )


def evaluate_reading(reading: MeterReading) -> list[MaintenanceAutomationExecution]:
    """Evalúa reglas activas en la misma transacción que registra la lectura."""
    rules = MaintenanceAutomationRule.query.filter_by(
        empresa_id=reading.empresa_id, meter_id=reading.meter_id, active=True
    ).order_by(MaintenanceAutomationRule.id).all()
    results = []
    value = Decimal(reading.value)
    for rule in rules:
        existing = MaintenanceAutomationExecution.query.filter_by(
            rule_id=rule.id, reading_id=reading.id
        ).first()
        if existing:
            results.append(existing); continue
        matched = _matches(value, rule.operator, Decimal(rule.threshold))
        if not matched:
            results.append(_execution(rule, reading, status="skipped", matched=False, reason="condition_not_met")); continue
        previous = _previous_reading(reading)
        if rule.crossing_only and previous is not None and _matches(
            Decimal(previous.value), rule.operator, Decimal(rule.threshold)
        ):
            results.append(_execution(rule, reading, status="skipped", matched=True, reason="no_threshold_crossing")); continue
        if rule.cooldown_minutes:
            cutoff = datetime.utcnow() - timedelta(minutes=rule.cooldown_minutes)
            recent = MaintenanceAutomationExecution.query.filter(
                MaintenanceAutomationExecution.rule_id == rule.id,
                MaintenanceAutomationExecution.status == "succeeded",
                MaintenanceAutomationExecution.evaluated_at >= cutoff,
            ).first()
            if recent:
                results.append(_execution(rule, reading, status="skipped", matched=True, reason="cooldown_active")); continue
        execution = _execution(rule, reading, status="succeeded", matched=True)
        try:
            _perform_action(rule, reading, execution)
            db.session.add(MaintenanceAutomationEvent(
                empresa_id=rule.empresa_id, rule_id=rule.id, execution_id=execution.id,
                event="automation_action_succeeded", actor_id=reading.recorded_by_user_id,
                detail=execution.action_snapshot,
            ))
        except (KeyError, TypeError, ValueError) as exc:
            execution.status = "failed"; execution.error = str(exc)[:500]
            db.session.add(MaintenanceAutomationEvent(
                empresa_id=rule.empresa_id, rule_id=rule.id, execution_id=execution.id,
                event="automation_action_failed", actor_id=reading.recorded_by_user_id,
                detail=execution.error,
            ))
        results.append(execution)
    return results
