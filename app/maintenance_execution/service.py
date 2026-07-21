"""Servicios de catálogo y versiones de procedimientos · Sprint 19.1."""

from __future__ import annotations

import json
import re
from datetime import datetime

from sqlalchemy import func, or_

from app import db
from app.models import MachineType, Technician, User, WorkOrder
from app.maintenance_execution.models import (
    MaintenanceProcedure,
    MaintenanceProcedureEvent,
    MaintenanceProcedureStep,
    MaintenanceProcedureVersion,
    PROCEDURE_RESPONSE_TYPES,
    PROCEDURE_VERSION_DRAFT,
    PROCEDURE_VERSION_PUBLISHED,
    PROCEDURE_VERSION_RETIRED,
    CHECKLIST_COMPLETED,
    CHECKLIST_IN_PROGRESS,
    CHECKLIST_PENDING,
    WorkOrderChecklist,
    WorkOrderChecklistEvent,
    WorkOrderChecklistEvidence,
    WorkOrderChecklistResponse,
    CHECKLIST_BLOCKED,
    CHECKLIST_REVIEWED,
)


_CODE_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,47}$")
_RESPONSE_TYPE_KEYS = frozenset(key for key, _label in PROCEDURE_RESPONSE_TYPES)


def _now() -> datetime:
    return datetime.utcnow()


def _normalize_code(raw: str, *, label: str) -> str:
    code = re.sub(r"\s+", "-", (raw or "").strip().upper())
    if not _CODE_RE.fullmatch(code):
        raise ValueError(
            f"{label} debe tener entre 2 y 48 caracteres: letras, números, guion o guion bajo."
        )
    return code


def _actor_for_tenant(empresa_id: int, actor_id: int) -> User:
    actor = User.query.filter_by(id=actor_id, empresa_id=empresa_id, activo=True).first()
    if not actor:
        raise ValueError("El usuario no pertenece a la empresa activa.")
    return actor


def _ensure_procedure_tenant(procedure: MaintenanceProcedure, empresa_id: int) -> None:
    if not procedure or procedure.empresa_id != empresa_id:
        raise ValueError("Procedimiento no disponible.")


def _ensure_version_tenant(
    version: MaintenanceProcedureVersion, empresa_id: int
) -> MaintenanceProcedure:
    procedure = version.procedure if version else None
    _ensure_procedure_tenant(procedure, empresa_id)
    return procedure


def _event(
    procedure: MaintenanceProcedure,
    actor_id: int,
    event: str,
    *,
    version: MaintenanceProcedureVersion | None = None,
    previous_status: str = "",
    new_status: str = "",
    detail: str = "",
) -> None:
    db.session.add(
        MaintenanceProcedureEvent(
            empresa_id=procedure.empresa_id,
            procedure=procedure,
            version_record=version,
            event=event,
            actor_id=actor_id,
            previous_status=previous_status,
            new_status=new_status,
            detail=(detail or "").strip()[:500],
        )
    )


def machine_types_for_tenant(empresa_id: int) -> list[MachineType]:
    return (
        MachineType.query.filter(
            MachineType.activo.is_(True),
            or_(MachineType.empresa_id == empresa_id, MachineType.empresa_id.is_(None)),
        )
        .order_by(MachineType.nombre.asc())
        .all()
    )


def _machine_type_for_tenant(empresa_id: int, raw_id) -> MachineType | None:
    if not raw_id:
        return None
    try:
        machine_type_id = int(raw_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("Selecciona un tipo de activo válido.") from exc
    machine_type = MachineType.query.filter(
        MachineType.id == machine_type_id,
        or_(MachineType.empresa_id == empresa_id, MachineType.empresa_id.is_(None)),
    ).first()
    if not machine_type:
        raise ValueError("El tipo de activo no pertenece a la empresa.")
    return machine_type


def create_procedure(
    empresa_id: int, actor_id: int, data
) -> tuple[MaintenanceProcedure, MaintenanceProcedureVersion]:
    _actor_for_tenant(empresa_id, actor_id)
    code = _normalize_code(data.get("code") or "", label="El código")
    name = (data.get("name") or "").strip()
    if len(name) < 3 or len(name) > 160:
        raise ValueError("El nombre debe tener entre 3 y 160 caracteres.")
    if MaintenanceProcedure.query.filter_by(empresa_id=empresa_id, code=code).first():
        raise ValueError("Ya existe un procedimiento con ese código.")

    machine_type = _machine_type_for_tenant(empresa_id, data.get("machine_type_id"))

    procedure = MaintenanceProcedure(
        empresa_id=empresa_id,
        code=code,
        name=name,
        description=(data.get("description") or "").strip(),
        machine_type=machine_type,
        created_by_id=actor_id,
    )
    version = MaintenanceProcedureVersion(
        procedure=procedure,
        version=1,
        status=PROCEDURE_VERSION_DRAFT,
        change_notes=(data.get("change_notes") or "Versión inicial").strip(),
        created_by_id=actor_id,
    )
    db.session.add(procedure)
    _event(
        procedure,
        actor_id,
        "procedure_created",
        version=version,
        new_status=PROCEDURE_VERSION_DRAFT,
        detail=f"Versión {version.version}",
    )
    return procedure, version


def update_procedure(
    procedure: MaintenanceProcedure, empresa_id: int, actor_id: int, data
) -> MaintenanceProcedure:
    _ensure_procedure_tenant(procedure, empresa_id)
    _actor_for_tenant(empresa_id, actor_id)
    code = _normalize_code(data.get("code") or "", label="El código")
    name = (data.get("name") or "").strip()
    if len(name) < 3 or len(name) > 160:
        raise ValueError("El nombre debe tener entre 3 y 160 caracteres.")
    duplicate = MaintenanceProcedure.query.filter(
        MaintenanceProcedure.empresa_id == empresa_id,
        MaintenanceProcedure.code == code,
        MaintenanceProcedure.id != procedure.id,
    ).first()
    if duplicate:
        raise ValueError("Ya existe un procedimiento con ese código.")

    before = f"{procedure.code} · {procedure.name}"
    procedure.code = code
    procedure.name = name
    procedure.description = (data.get("description") or "").strip()
    procedure.machine_type = _machine_type_for_tenant(
        empresa_id, data.get("machine_type_id")
    )
    procedure.active = str(data.get("active", "0")).lower() in {
        "1", "true", "yes", "si", "sí", "on"
    }
    procedure.updated_at = _now()
    _event(
        procedure,
        actor_id,
        "procedure_updated",
        detail=f"{before} → {procedure.code} · {procedure.name}",
    )
    return procedure


def _parse_config(raw, position: int) -> str:
    text = (raw or "").strip() or "{}"
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"La configuración JSON del paso {position} no es válida.") from exc
    if not isinstance(value, dict):
        raise ValueError(f"La configuración del paso {position} debe ser un objeto JSON.")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def save_draft_version(
    version: MaintenanceProcedureVersion,
    empresa_id: int,
    actor_id: int,
    data,
    steps: list[dict],
) -> MaintenanceProcedureVersion:
    procedure = _ensure_version_tenant(version, empresa_id)
    _actor_for_tenant(empresa_id, actor_id)
    if version.status != PROCEDURE_VERSION_DRAFT:
        raise ValueError("Una versión publicada o retirada es inmutable.")

    parsed: list[MaintenanceProcedureStep] = []
    seen_codes: set[str] = set()
    for position, item in enumerate(steps, start=1):
        title = (item.get("title") or "").strip()
        if not title:
            continue
        if len(title) > 180:
            raise ValueError(f"El título del paso {position} supera 180 caracteres.")
        code = _normalize_code(
            item.get("code") or f"STEP-{position:03d}", label=f"El código del paso {position}"
        )
        if code in seen_codes:
            raise ValueError(f"El código {code} está repetido en la versión.")
        seen_codes.add(code)
        response_type = (item.get("response_type") or "confirmation").strip()
        if response_type not in _RESPONSE_TYPE_KEYS:
            raise ValueError(f"El tipo de respuesta del paso {position} no es válido.")
        parsed.append(
            MaintenanceProcedureStep(
                position=position,
                code=code,
                title=title,
                instructions=(item.get("instructions") or "").strip(),
                response_type=response_type,
                required=str(item.get("required", "1")).lower()
                in {"1", "true", "yes", "si", "sí", "on"},
                config_json=_parse_config(item.get("config_json"), position),
            )
        )
    if not parsed:
        raise ValueError("Agrega al menos un paso al procedimiento.")

    version.change_notes = (data.get("change_notes") or "").strip()[:500]
    version.steps.clear()
    # Materializa los DELETE antes de insertar códigos/posiciones reutilizados.
    # De lo contrario, SQLite puede evaluar primero los INSERT y violar los
    # índices únicos aun cuando el reemplazo sea válido dentro de la transacción.
    db.session.flush()
    version.steps.extend(parsed)
    version.updated_at = _now()
    procedure.updated_at = version.updated_at
    _event(
        procedure,
        actor_id,
        "draft_saved",
        version=version,
        previous_status=PROCEDURE_VERSION_DRAFT,
        new_status=PROCEDURE_VERSION_DRAFT,
        detail=f"{len(parsed)} paso(s)",
    )
    return version


def create_draft_version(
    procedure: MaintenanceProcedure, empresa_id: int, actor_id: int
) -> MaintenanceProcedureVersion:
    _ensure_procedure_tenant(procedure, empresa_id)
    _actor_for_tenant(empresa_id, actor_id)
    existing = MaintenanceProcedureVersion.query.filter_by(
        procedure_id=procedure.id, status=PROCEDURE_VERSION_DRAFT
    ).first()
    if existing:
        return existing

    last_number = (
        db.session.query(func.max(MaintenanceProcedureVersion.version))
        .filter_by(procedure_id=procedure.id)
        .scalar()
        or 0
    )
    source = (
        MaintenanceProcedureVersion.query.filter_by(procedure_id=procedure.id)
        .filter(
            MaintenanceProcedureVersion.status.in_(
                [PROCEDURE_VERSION_PUBLISHED, PROCEDURE_VERSION_RETIRED]
            )
        )
        .order_by(MaintenanceProcedureVersion.version.desc())
        .first()
    )
    version = MaintenanceProcedureVersion(
        procedure=procedure,
        version=last_number + 1,
        status=PROCEDURE_VERSION_DRAFT,
        change_notes="",
        created_by_id=actor_id,
    )
    if source:
        for item in source.steps:
            version.steps.append(
                MaintenanceProcedureStep(
                    position=item.position,
                    code=item.code,
                    title=item.title,
                    instructions=item.instructions,
                    response_type=item.response_type,
                    required=item.required,
                    config_json=item.config_json,
                )
            )
    db.session.add(version)
    procedure.updated_at = _now()
    _event(
        procedure,
        actor_id,
        "draft_created",
        version=version,
        new_status=PROCEDURE_VERSION_DRAFT,
        detail=f"Versión {version.version} desde v{source.version if source else 'vacía'}",
    )
    return version


def publish_version(
    version: MaintenanceProcedureVersion, empresa_id: int, actor_id: int
) -> MaintenanceProcedureVersion:
    procedure = _ensure_version_tenant(version, empresa_id)
    _actor_for_tenant(empresa_id, actor_id)
    if version.status != PROCEDURE_VERSION_DRAFT:
        raise ValueError("Solo una versión en borrador puede publicarse.")
    if not version.steps:
        raise ValueError("No se puede publicar un procedimiento sin pasos.")

    now = _now()
    previous_versions = MaintenanceProcedureVersion.query.filter(
        MaintenanceProcedureVersion.procedure_id == procedure.id,
        MaintenanceProcedureVersion.status == PROCEDURE_VERSION_PUBLISHED,
        MaintenanceProcedureVersion.id != version.id,
    ).all()
    for previous in previous_versions:
        previous.status = PROCEDURE_VERSION_RETIRED
        previous.retired_at = now
        _event(
            procedure,
            actor_id,
            "version_retired",
            version=previous,
            previous_status=PROCEDURE_VERSION_PUBLISHED,
            new_status=PROCEDURE_VERSION_RETIRED,
            detail=f"Retirada al publicar v{version.version}",
        )

    version.status = PROCEDURE_VERSION_PUBLISHED
    version.published_by_id = actor_id
    version.published_at = now
    version.retired_at = None
    procedure.updated_at = now
    _event(
        procedure,
        actor_id,
        "version_published",
        version=version,
        previous_status=PROCEDURE_VERSION_DRAFT,
        new_status=PROCEDURE_VERSION_PUBLISHED,
        detail=f"Versión {version.version} · {len(version.steps)} paso(s)",
    )
    return version


def retire_version(
    version: MaintenanceProcedureVersion, empresa_id: int, actor_id: int
) -> MaintenanceProcedureVersion:
    procedure = _ensure_version_tenant(version, empresa_id)
    _actor_for_tenant(empresa_id, actor_id)
    if version.status != PROCEDURE_VERSION_PUBLISHED:
        raise ValueError("Solo una versión publicada puede retirarse.")
    version.status = PROCEDURE_VERSION_RETIRED
    version.retired_at = _now()
    procedure.updated_at = version.retired_at
    _event(
        procedure,
        actor_id,
        "version_retired",
        version=version,
        previous_status=PROCEDURE_VERSION_PUBLISHED,
        new_status=PROCEDURE_VERSION_RETIRED,
        detail=f"Versión {version.version}",
    )
    return version


def published_procedures_for_work_order(work_order: WorkOrder):
    return (
        MaintenanceProcedureVersion.query.join(MaintenanceProcedure)
        .filter(
            MaintenanceProcedure.empresa_id == work_order.empresa_id,
            MaintenanceProcedure.active.is_(True),
            MaintenanceProcedureVersion.status == PROCEDURE_VERSION_PUBLISHED,
            or_(
                MaintenanceProcedure.machine_type_id.is_(None),
                MaintenanceProcedure.machine_type_id == work_order.machine.machine_type_id,
            ),
        )
        .order_by(MaintenanceProcedure.code, MaintenanceProcedureVersion.version.desc())
        .all()
    )


def _checklist_event(checklist, actor_id, event, detail=""):
    db.session.add(WorkOrderChecklistEvent(
        empresa_id=checklist.empresa_id, checklist=checklist, event=event,
        actor_id=actor_id, detail=(detail or "")[:500],
    ))


def assign_checklist(work_order: WorkOrder, version_id: int, actor_id: int):
    actor = _actor_for_tenant(work_order.empresa_id, actor_id)
    if actor.rol not in {"admin", "superadmin", "supervisor"}:
        raise ValueError("No tienes permiso para asignar procedimientos.")
    if work_order.execution_checklist:
        raise ValueError("La OT ya tiene un checklist histórico asignado.")
    if not work_order.technician_id:
        raise ValueError("Asigna primero un técnico interno a la OT.")
    technician = Technician.query.filter_by(
        id=work_order.technician_id, empresa_id=work_order.empresa_id, activo=True
    ).first()
    if not technician or not technician.user or not technician.user.activo:
        raise ValueError("El técnico asignado debe tener un usuario activo vinculado.")
    allowed = {item.id: item for item in published_procedures_for_work_order(work_order)}
    version = allowed.get(int(version_id or 0))
    if not version:
        raise ValueError("Selecciona una versión publicada aplicable al activo.")
    procedure = version.procedure
    checklist = WorkOrderChecklist(
        empresa_id=work_order.empresa_id,
        work_order=work_order,
        procedure_version=version,
        assigned_technician=technician,
        procedure_code_snapshot=procedure.code,
        procedure_name_snapshot=procedure.name,
        version_snapshot=version.version,
        created_by_id=actor_id,
    )
    db.session.add(checklist)
    _checklist_event(checklist, actor_id, "checklist_assigned", f"{procedure.code} v{version.version}")
    return checklist


def can_access_checklist(checklist, user) -> bool:
    if not user or not getattr(user, "is_authenticated", False):
        return False
    if user.empresa_id != checklist.empresa_id:
        return False
    if user.rol in {"admin", "superadmin", "supervisor"}:
        return True
    return bool(
        user.rol == "tecnico"
        and checklist.assigned_technician
        and checklist.assigned_technician.user_id == user.id
    )


def _validated_step_value(step, raw: str):
    value = (raw or "").strip()
    if step.response_type == "evidence":
        return value, False
    if step.response_type == "signature":
        return value, value == "confirmed"
    if step.response_type == "confirmation":
        return value, value in {"done", "not_done", "not_applicable"}
    if step.response_type in {"number", "measurement"}:
        if not value:
            return value, False
        try:
            float(value.replace(",", "."))
        except ValueError:
            raise ValueError(f"{step.title}: ingresa un valor numérico válido.")
        return value, True
    return value, bool(value)


def _response_conformity(step, value: str, values: dict) -> tuple[str, str]:
    requested = (values.get(f"conformity_{step.id}") or "").strip()
    justification = (values.get(f"justification_{step.id}") or "").strip()[:500]
    if step.response_type == "confirmation":
        requested = {
            "done": "conforming",
            "not_done": "nonconforming",
            "not_applicable": "not_applicable",
        }.get(value, "pending_review")
    elif step.response_type in {"signature", "evidence"}:
        requested = "conforming" if value else "pending_review"
    elif not requested:
        requested = "conforming"
    if requested not in {"conforming", "nonconforming", "not_applicable", "pending_review"}:
        requested = "pending_review"
    if requested in {"nonconforming", "not_applicable"} and not justification:
        raise ValueError(f"{step.title}: registra una justificación.")
    return requested, justification


def recompute_checklist(checklist):
    responses = {item.step_id: item for item in checklist.responses}
    required_valid = all(
        responses.get(step.id) and responses[step.id].is_valid
        for step in checklist.procedure_version.steps if step.required
    )
    unresolved = any(
        item.conformity in {"nonconforming", "pending_review"}
        and not item.resolved_at
        for item in checklist.responses
    )
    previous = checklist.status
    if unresolved:
        checklist.status = CHECKLIST_BLOCKED
    elif required_valid:
        checklist.status = CHECKLIST_COMPLETED
    elif checklist.responses:
        checklist.status = CHECKLIST_IN_PROGRESS
    else:
        checklist.status = CHECKLIST_PENDING
    now = _now()
    checklist.started_at = checklist.started_at or (now if checklist.responses else None)
    checklist.completed_at = now if checklist.status == CHECKLIST_COMPLETED else None
    checklist.updated_at = now
    return previous


def save_checklist_responses(checklist, actor_id: int, values: dict):
    actor = _actor_for_tenant(checklist.empresa_id, actor_id)
    if not can_access_checklist(checklist, actor):
        raise ValueError("No tienes acceso a este checklist.")
    if (checklist.work_order.status or "").strip().lower() in {"completado", "cerrada"}:
        raise ValueError("La OT está finalizada y su checklist es histórico de solo lectura.")
    performer = checklist.assigned_technician.user
    if not performer or not performer.activo:
        raise ValueError("El técnico ejecutor no tiene un usuario activo.")
    existing = {item.step_id: item for item in checklist.responses}
    changed = 0
    for step in checklist.procedure_version.steps:
        key = f"step_{step.id}"
        if key not in values:
            continue
        value, valid = _validated_step_value(step, values.get(key))
        if not step.required and not value and not existing.get(step.id):
            continue
        if step.response_type == "signature" and valid and actor.id != performer.id:
            raise ValueError(f"{step.title}: la firma debe confirmarla el técnico asignado.")
        conformity, justification = _response_conformity(step, value, values)
        response = existing.get(step.id)
        payload = json.dumps({"value": value}, ensure_ascii=False)
        if response:
            response.value_json = payload
            response.is_valid = valid
            response.performed_by_user_id = performer.id
            response.recorded_by_user_id = actor.id
            response.conformity = conformity
            response.justification = justification
            response.resolution_note = ""
            response.resolved_by_id = None
            response.resolved_at = None
            response.updated_at = _now()
        else:
            response = WorkOrderChecklistResponse(
                checklist=checklist, step=step, value_json=payload, is_valid=valid,
                performed_by_user_id=performer.id, recorded_by_user_id=actor.id,
                conformity=conformity, justification=justification,
            )
            db.session.add(response)
        if step.response_type == "signature" and valid:
            response.signed_at = _now()
            response.signature_name_snapshot = performer.etiqueta()
            response.signature_purpose = "Confirmación de ejecución del paso"
        changed += 1
    db.session.flush()
    previous = recompute_checklist(checklist)
    event = "checklist_completed" if checklist.status == CHECKLIST_COMPLETED else "checklist_responses_saved"
    _checklist_event(checklist, actor.id, event, f"{changed} respuesta(s); {previous} → {checklist.status}")
    return checklist


def response_for_evidence(checklist, step, actor_id: int):
    actor = _actor_for_tenant(checklist.empresa_id, actor_id)
    if not can_access_checklist(checklist, actor):
        raise ValueError("No tienes acceso a este checklist.")
    if step.version_id != checklist.procedure_version_id or step.response_type != "evidence":
        raise ValueError("El paso no admite evidencias.")
    performer = checklist.assigned_technician.user
    response = WorkOrderChecklistResponse.query.filter_by(
        checklist_id=checklist.id, step_id=step.id
    ).first()
    if not response:
        response = WorkOrderChecklistResponse(
            checklist=checklist, step=step, value_json='{"value":"evidence"}',
            is_valid=False, conformity="conforming",
            performed_by_user_id=performer.id, recorded_by_user_id=actor.id,
        )
        db.session.add(response)
        db.session.flush()
    return response, actor, performer


def register_evidence_metadata(response, actor_id: int, *, storage_key: str, original_name: str, mime_type: str, size_bytes: int, checksum: str):
    evidence = WorkOrderChecklistEvidence(
        empresa_id=response.checklist.empresa_id, checklist=response.checklist,
        response=response, step_id=response.step_id, storage_key=storage_key,
        original_name=original_name, mime_type=mime_type, size_bytes=size_bytes,
        checksum_sha256=checksum, uploaded_by_id=actor_id,
    )
    db.session.add(evidence)
    db.session.flush()
    response.is_valid = True
    response.recorded_by_user_id = actor_id
    response.updated_at = _now()
    previous = recompute_checklist(response.checklist)
    _checklist_event(response.checklist, actor_id, "evidence_uploaded", f"{response.step.code} · {original_name}; {previous} → {response.checklist.status}")
    return evidence


def review_checklist(checklist, actor_id: int, values: dict):
    actor = _actor_for_tenant(checklist.empresa_id, actor_id)
    if actor.rol not in {"admin", "superadmin", "supervisor"}:
        raise ValueError("Solo un supervisor o administrador puede revisar.")
    if checklist.required_completed != checklist.required_total:
        raise ValueError("No se puede revisar: faltan pasos obligatorios.")
    for response in checklist.responses:
        if response.conformity in {"nonconforming", "pending_review"} and not response.resolved_at:
            note = (values.get(f"resolution_{response.id}") or "").strip()[:500]
            if not note:
                raise ValueError(f"Registra la resolución de: {response.step.title}.")
            response.resolution_note = note
            response.resolved_by_id = actor.id
            response.resolved_at = _now()
    recompute_checklist(checklist)
    if checklist.status != CHECKLIST_COMPLETED:
        raise ValueError("El checklist aún contiene bloqueos sin resolver.")
    checklist.status = CHECKLIST_REVIEWED
    checklist.reviewed_by_id = actor.id
    checklist.reviewed_at = _now()
    checklist.review_notes = (values.get("review_notes") or "").strip()[:500]
    _checklist_event(checklist, actor.id, "checklist_reviewed", checklist.review_notes)
    return checklist


def checklist_completion_error(work_order: WorkOrder) -> str | None:
    checklist = work_order.execution_checklist
    if checklist and checklist.status != CHECKLIST_REVIEWED:
        return (
            f"El checklist requiere revisión ({checklist.required_completed}/"
            f"{checklist.required_total} pasos obligatorios; estado {checklist.status})."
        )
    return None
