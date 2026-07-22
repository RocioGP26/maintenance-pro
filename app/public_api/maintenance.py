"""API pública Maintenance: incidencias, OT, medidores y lecturas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from flask import Blueprint, g, request

from app import db, limiter
from app.incident_notifications import create_incident_notifications
from app.integrations.authorization import scope_required
from app.maintenance_execution.meter_service import record_reading
from app.maintenance_execution.models import AssetMeter, MeterReading
from app.models import (
    INCIDENT_PRIORIDADES,
    INCIDENT_TIPOS,
    Incident,
    IncidentHistory,
    Machine,
    User,
    WorkOrder,
)
from app.public_api.contract import (
    PUBLIC_API_LIMIT,
    ApiContractError,
    api_rate_key,
    idempotency_lookup,
    iso_utc,
    pagination_meta,
    parse_datetime_parameter,
    parse_pagination,
    replay_idempotency,
    store_idempotency,
    success,
)
from app.tenancy.decorators import tenant_required
from app.tenancy.queries import query_tenant


public_maintenance_bp = Blueprint("public_maintenance", __name__)


@dataclass
class _IntegrationActor:
    empresa_id: int
    id: int | None = None
    rol: str = "integration"
    is_authenticated: bool = True
    is_integration: bool = True


def _actor():
    if getattr(g, "auth_type", None) == "api_key":
        return _IntegrationActor(int(g.empresa_id))
    user = db.session.get(User, int(g.user_id)) if getattr(g, "user_id", None) else None
    if user is None or not user.activo or user.bloqueado:
        raise ApiContractError("AUTHENTICATION_REQUIRED", "Usuario activo requerido.", 401)
    return user


def _incident_item(item: Incident) -> dict:
    return {
        "incident_id": item.id,
        "number": item.numero,
        "title": item.titulo,
        "description": item.descripcion or "",
        "asset_id": item.machine_id,
        "reported_by": item.reportado_por or "",
        "reporter_area": item.area or "",
        "responsible_area": item.area_responsable or "",
        "location": item.ubicacion or "",
        "type": item.tipo or "",
        "priority": item.prioridad or "media",
        "status": item.estado or "reportado",
        "equipment_stopped": bool(item.equipo_detenido),
        "event_date": item.fecha_evento.isoformat() if item.fecha_evento else None,
        "event_time": item.hora_evento or None,
        "reported_at": iso_utc(item.reportado_en),
        "updated_at": iso_utc(item.updated_at),
        "work_order_id": item.work_order_id,
    }


def _work_order_item(item: WorkOrder) -> dict:
    statuses = {
        "programada": "scheduled", "abierta": "open", "en_proceso": "in_progress",
        "vencida": "overdue", "completado": "completed", "cerrada": "closed",
    }
    return {
        "work_order_id": item.id,
        "asset_id": item.machine_id,
        "number": item.numero,
        "title": item.titulo,
        "description": item.descripcion or "",
        "type": item.tipo,
        "status": statuses.get((item.status or "").lower(), item.status),
        "priority": item.prioridad,
        "scheduled_date": item.fecha_programada.isoformat() if item.fecha_programada else None,
        "started_at": iso_utc(item.fecha_inicio),
        "closed_at": iso_utc(item.fecha_cierre),
        "created_at": iso_utc(item.created_at),
        "updated_at": iso_utc(item.updated_at),
    }


def _meter_item(item: AssetMeter) -> dict:
    latest = item.latest_reading
    return {
        "meter_id": item.id,
        "asset_id": item.machine_id,
        "code": item.code,
        "name": item.name,
        "type": item.meter_type,
        "unit": item.unit,
        "decimals": item.decimals,
        "active": bool(item.active),
        "rules": item.rules,
        "latest_reading": _reading_item(latest) if latest else None,
        "updated_at": iso_utc(item.updated_at),
    }


def _reading_item(item: MeterReading) -> dict:
    return {
        "reading_id": item.id,
        "meter_id": item.meter_id,
        "work_order_id": item.work_order_id,
        "value": format(item.value, "f"),
        "measured_at": iso_utc(item.measured_at),
        "source": item.source,
        "notes": item.notes or "",
        "flagged": bool(item.flagged),
        "anomaly_type": item.anomaly_type or None,
        "justification": item.justification or None,
        "created_at": iso_utc(item.created_at),
    }


def _next_incident_number() -> str:
    prefix = f"INC-{date.today().year % 100:02d}-"
    last = query_tenant(Incident).filter(Incident.numero.like(f"{prefix}%")).order_by(
        Incident.id.desc()
    ).first()
    try:
        sequence = int(last.numero.rsplit("-", 1)[1]) + 1 if last and last.numero else 1
    except (ValueError, IndexError):
        sequence = 1
    return f"{prefix}{sequence:04d}"


@public_maintenance_bp.route("/api/v1/maintenance/incidents", methods=["GET", "POST"])
@tenant_required
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def incidents():
    if request.method == "GET":
        return _incidents_list()
    return _incident_create()


@scope_required("maintenance.incidents:read")
def _incidents_list():
    page, page_size = parse_pagination({"status", "priority", "asset_id", "updated_since"})
    query = query_tenant(Incident)
    if request.args.get("status"):
        query = query.filter(Incident.estado == request.args["status"].strip().lower())
    if request.args.get("priority"):
        query = query.filter(Incident.prioridad == request.args["priority"].strip().lower())
    if request.args.get("asset_id"):
        try:
            query = query.filter(Incident.machine_id == int(request.args["asset_id"]))
        except ValueError as exc:
            raise ApiContractError("INVALID_PARAMETER", "asset_id debe ser entero.") from exc
    since = parse_datetime_parameter(request.args.get("updated_since"), "updated_since")
    if since:
        query = query.filter(Incident.updated_at >= since)
    total = query.count()
    items = query.order_by(Incident.updated_at.desc(), Incident.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success(
        [_incident_item(item) for item in items],
        pagination=pagination_meta(total, page, page_size),
    )


@scope_required("maintenance.incidents:write")
def _incident_create():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ApiContractError("INVALID_BODY", "Se requiere un objeto JSON.")
    record, key, digest, actor_key, credential_id = idempotency_lookup(
        "maintenance.incidents.create", payload
    )
    if record:
        return replay_idempotency(record)
    required = ("title", "description", "responsible_area", "type")
    missing = [name for name in required if not str(payload.get(name) or "").strip()]
    if missing:
        raise ApiContractError(
            "VALIDATION_ERROR", "Faltan campos obligatorios.", details={"fields": missing}
        )
    valid_types = {value for value, _label in INCIDENT_TIPOS}
    incident_type = str(payload["type"]).strip().lower()
    if incident_type not in valid_types:
        raise ApiContractError("VALIDATION_ERROR", "type no es válido.", details={"field": "type"})
    priority = str(payload.get("priority") or "media").strip().lower()
    if priority not in {value for value, _label in INCIDENT_PRIORIDADES}:
        raise ApiContractError("VALIDATION_ERROR", "priority no es válida.", details={"field": "priority"})
    machine = None
    if payload.get("asset_id") is not None:
        try:
            machine = query_tenant(Machine).filter_by(id=int(payload["asset_id"])).first()
        except (TypeError, ValueError) as exc:
            raise ApiContractError("VALIDATION_ERROR", "asset_id debe ser entero.") from exc
        if machine is None:
            raise ApiContractError("RESOURCE_NOT_FOUND", "Activo no encontrado.", 404)
    event_date = None
    if payload.get("event_date"):
        try:
            event_date = date.fromisoformat(str(payload["event_date"]))
        except ValueError as exc:
            raise ApiContractError("VALIDATION_ERROR", "event_date debe usar YYYY-MM-DD.") from exc
    event_time = str(payload.get("event_time") or "").strip()
    if event_time:
        try:
            datetime.strptime(event_time, "%H:%M")
        except ValueError as exc:
            raise ApiContractError("VALIDATION_ERROR", "event_time debe usar HH:MM.") from exc
    equipment_stopped = payload.get("equipment_stopped", False)
    if not isinstance(equipment_stopped, bool):
        raise ApiContractError("VALIDATION_ERROR", "equipment_stopped debe ser booleano.")
    actor = _actor()
    reporter = str(payload.get("reported_by") or "").strip()
    if not reporter:
        reporter = actor.etiqueta() if isinstance(actor, User) else f"Integración {actor_key}"
    item = Incident(
        empresa_id=g.empresa_id,
        numero=_next_incident_number(),
        titulo=str(payload["title"]).strip()[:200],
        descripcion=str(payload["description"]).strip(),
        machine_id=machine.id if machine else None,
        user_id=actor.id,
        reportado_por=reporter[:200],
        area=str(payload.get("reporter_area") or "Integración").strip()[:120],
        area_responsable=str(payload["responsible_area"]).strip()[:120],
        ubicacion=str(payload.get("location") or (machine.ubicacion if machine else "")).strip()[:200],
        tipo=incident_type,
        prioridad=priority,
        equipo_detenido=equipment_stopped,
        fecha_evento=event_date,
        hora_evento=event_time,
    )
    db.session.add(item)
    db.session.flush()
    db.session.add(
        IncidentHistory(
            incident_id=item.id,
            user_id=actor.id,
            accion="reported_via_api",
            estado_anterior="",
            estado_nuevo="reportado",
            comentario=f"Asignado al área {item.area_responsable}",
        )
    )
    create_incident_notifications(item)
    response_data = _incident_item(item)
    store_idempotency(
        operation="maintenance.incidents.create",
        key=key,
        digest=digest,
        actor_key=actor_key,
        credential_id=credential_id,
        resource_type="incident",
        resource_id=item.id,
        response_data=response_data,
    )
    db.session.commit()
    return success(response_data, status=201)


@public_maintenance_bp.get("/api/v1/maintenance/incidents/<int:incident_id>")
@tenant_required
@scope_required("maintenance.incidents:read")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def incident_detail(incident_id: int):
    item = query_tenant(Incident).filter_by(id=incident_id).first()
    if item is None:
        raise ApiContractError("RESOURCE_NOT_FOUND", "Incidencia no encontrada.", 404)
    return success(_incident_item(item))


@public_maintenance_bp.get("/api/v1/maintenance/work-orders/<int:work_order_id>")
@tenant_required
@scope_required("maintenance.work_orders:read")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def work_order_detail(work_order_id: int):
    item = query_tenant(WorkOrder).filter_by(id=work_order_id).first()
    if item is None:
        raise ApiContractError("RESOURCE_NOT_FOUND", "Orden de trabajo no encontrada.", 404)
    return success(_work_order_item(item))


@public_maintenance_bp.get("/api/v1/maintenance/assets/<int:asset_id>/meters")
@tenant_required
@scope_required("maintenance.meters:read")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def asset_meters(asset_id: int):
    machine = query_tenant(Machine).filter_by(id=asset_id).first()
    if machine is None:
        raise ApiContractError("RESOURCE_NOT_FOUND", "Activo no encontrado.", 404)
    page, page_size = parse_pagination({"active", "updated_since"})
    query = query_tenant(AssetMeter).filter_by(machine_id=machine.id)
    if request.args.get("active"):
        raw = request.args["active"].strip().lower()
        if raw not in {"true", "false"}:
            raise ApiContractError("INVALID_PARAMETER", "active debe ser true o false.")
        query = query.filter(AssetMeter.active.is_(raw == "true"))
    since = parse_datetime_parameter(request.args.get("updated_since"), "updated_since")
    if since:
        query = query.filter(AssetMeter.updated_at >= since)
    total = query.count()
    items = query.order_by(AssetMeter.updated_at.desc(), AssetMeter.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success([_meter_item(item) for item in items], pagination=pagination_meta(total, page, page_size))


@public_maintenance_bp.route("/api/v1/maintenance/meters/<int:meter_id>/readings", methods=["GET", "POST"])
@tenant_required
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def meter_readings(meter_id: int):
    meter = query_tenant(AssetMeter).filter_by(id=meter_id).first()
    if meter is None:
        raise ApiContractError("RESOURCE_NOT_FOUND", "Medidor no encontrado.", 404)
    if request.method == "GET":
        return _readings_list(meter)
    return _reading_create(meter)


@scope_required("maintenance.meters:read")
def _readings_list(meter: AssetMeter):
    page, page_size = parse_pagination({"measured_since", "measured_until"})
    query = query_tenant(MeterReading).filter_by(meter_id=meter.id)
    since = parse_datetime_parameter(request.args.get("measured_since"), "measured_since")
    until = parse_datetime_parameter(request.args.get("measured_until"), "measured_until")
    if since:
        query = query.filter(MeterReading.measured_at >= since)
    if until:
        query = query.filter(MeterReading.measured_at <= until)
    total = query.count()
    items = query.order_by(MeterReading.measured_at.desc(), MeterReading.id.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()
    return success([_reading_item(item) for item in items], pagination=pagination_meta(total, page, page_size))


@scope_required("maintenance.meters:write")
def _reading_create(meter: AssetMeter):
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ApiContractError("INVALID_BODY", "Se requiere un objeto JSON.")
    record, key, digest, actor_key, credential_id = idempotency_lookup(
        f"maintenance.meters.{meter.id}.readings.create", payload
    )
    if record:
        return replay_idempotency(record)
    if payload.get("value") in (None, ""):
        raise ApiContractError("VALIDATION_ERROR", "value es obligatorio.", details={"field": "value"})
    try:
        item = record_reading(meter, _actor(), payload)
    except (TypeError, ValueError) as exc:
        raise ApiContractError("VALIDATION_ERROR", str(exc)) from exc
    response_data = _reading_item(item)
    store_idempotency(
        operation=f"maintenance.meters.{meter.id}.readings.create",
        key=key,
        digest=digest,
        actor_key=actor_key,
        credential_id=credential_id,
        resource_type="meter_reading",
        resource_id=item.id,
        response_data=response_data,
    )
    db.session.commit()
    return success(response_data, status=201)
