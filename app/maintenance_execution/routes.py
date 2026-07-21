"""UI del catálogo de procedimientos · Sprint 19.1."""

from __future__ import annotations

import json
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import selectinload

from app import db
from app.models import Machine, User, WorkOrder
from app.module_guard import require_module
from app.modules import MODULO_MANTENIMIENTO
from app.permissions import (
    can_manage_maintenance_procedures,
    can_publish_maintenance_procedures,
    can_view_maintenance_procedures,
)
from app.maintenance_execution.models import (
    MaintenanceProcedure,
    MaintenanceProcedureVersion,
    PROCEDURE_RESPONSE_TYPES,
    PROCEDURE_VERSION_PUBLISHED,
    WorkOrderChecklist,
    WorkOrderChecklistEvidence,
    WorkOrderChecklistEvent,
    MaintenanceLogAttachment,
    MaintenanceLogEntry,
    MaintenanceLogNotification,
    AssetMeter,
    METER_TYPES,
)
from app.maintenance_execution.service import (
    create_draft_version,
    create_procedure,
    machine_types_for_tenant,
    publish_version,
    retire_version,
    save_draft_version,
    update_procedure,
    assign_checklist,
    can_access_checklist,
    published_procedures_for_work_order,
    save_checklist_responses,
    register_evidence_metadata,
    response_for_evidence,
    review_checklist,
)
from app.maintenance_execution.evidence import resolve_evidence_path, save_evidence_file
from app.maintenance_execution.log_service import (
    attach_log_file, audit_log_access, can_view_log, can_write_log,
    create_log_entry, entries_for_context, log_notifications_for_user,
    mark_log_notification_read, resolve_log_context,
)
from app.maintenance_execution.log_storage import resolve_log_file, save_log_file
from app.maintenance_execution.meter_service import (
    can_manage_meters,
    can_record_reading,
    can_view_meters,
    create_meter,
    meters_for_machine,
    performers_for_meter,
    record_reading,
    set_meter_active,
)


maintenance_execution_bp = Blueprint(
    "maintenance_execution", __name__, url_prefix="/maintenance/procedures"
)


def _empresa_id() -> int:
    value = getattr(current_user, "empresa_id", None)
    if value is None:
        abort(403)
    return int(value)


def _manager_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not can_manage_maintenance_procedures(current_user):
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _publisher_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not can_publish_maintenance_procedures(current_user):
            abort(403)
        return view(*args, **kwargs)

    return wrapped


def _procedure_query():
    return MaintenanceProcedure.query.filter_by(empresa_id=_empresa_id())


def _procedure_or_404(procedure_id: int) -> MaintenanceProcedure:
    return (
        _procedure_query()
        .options(
            selectinload(MaintenanceProcedure.versions).selectinload(
                MaintenanceProcedureVersion.steps
            ),
            selectinload(MaintenanceProcedure.events),
        )
        .filter_by(id=procedure_id)
        .first_or_404()
    )


def _version_or_404(procedure_id: int, version_id: int) -> MaintenanceProcedureVersion:
    procedure = _procedure_or_404(procedure_id)
    version = next((item for item in procedure.versions if item.id == version_id), None)
    if version is None:
        abort(404)
    return version


def _steps_from_form() -> list[dict]:
    codes = request.form.getlist("step_code")
    titles = request.form.getlist("step_title")
    instructions = request.form.getlist("step_instructions")
    response_types = request.form.getlist("step_response_type")
    required_values = request.form.getlist("step_required")
    configs = request.form.getlist("step_config_json")
    width = max(
        len(codes),
        len(titles),
        len(instructions),
        len(response_types),
        len(required_values),
        len(configs),
        0,
    )
    return [
        {
            "code": codes[i] if i < len(codes) else "",
            "title": titles[i] if i < len(titles) else "",
            "instructions": instructions[i] if i < len(instructions) else "",
            "response_type": response_types[i] if i < len(response_types) else "confirmation",
            "required": required_values[i] if i < len(required_values) else "1",
            "config_json": configs[i] if i < len(configs) else "{}",
        }
        for i in range(width)
    ]


@maintenance_execution_bp.route("/")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def procedures_list():
    if not can_view_maintenance_procedures(current_user):
        abort(403)
    query = _procedure_query().options(selectinload(MaintenanceProcedure.versions))
    if not can_manage_maintenance_procedures(current_user):
        query = query.join(MaintenanceProcedureVersion).filter(
            MaintenanceProcedure.active.is_(True),
            MaintenanceProcedureVersion.status == PROCEDURE_VERSION_PUBLISHED
        ).distinct()
    items = query.order_by(MaintenanceProcedure.code.asc()).all()
    return render_template(
        "maintenance_execution/procedures_list.html",
        items=items,
        can_manage=can_manage_maintenance_procedures(current_user),
    )


@maintenance_execution_bp.route("/new", methods=["GET", "POST"])
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def procedures_new():
    if request.method == "POST":
        try:
            procedure, version = create_procedure(
                _empresa_id(), current_user.id, request.form
            )
            db.session.commit()
            flash("Procedimiento creado. Agrega los pasos de la versión inicial.", "success")
            return redirect(
                url_for(
                    "maintenance_execution.version_edit",
                    procedure_id=procedure.id,
                    version_id=version.id,
                )
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template(
        "maintenance_execution/procedure_form.html",
        machine_types=machine_types_for_tenant(_empresa_id()),
        procedure=None,
    )


@maintenance_execution_bp.route("/<int:procedure_id>/edit", methods=["GET", "POST"])
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def procedure_edit(procedure_id: int):
    procedure = _procedure_or_404(procedure_id)
    if request.method == "POST":
        try:
            update_procedure(procedure, _empresa_id(), current_user.id, request.form)
            db.session.commit()
            flash("Datos del procedimiento actualizados.", "success")
            return redirect(
                url_for(
                    "maintenance_execution.procedure_detail",
                    procedure_id=procedure.id,
                )
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template(
        "maintenance_execution/procedure_form.html",
        machine_types=machine_types_for_tenant(_empresa_id()),
        procedure=procedure,
    )


@maintenance_execution_bp.route("/<int:procedure_id>")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def procedure_detail(procedure_id: int):
    procedure = _procedure_or_404(procedure_id)
    can_manage = can_manage_maintenance_procedures(current_user)
    if not can_manage and (
        not procedure.active
        or not any(
            item.status == PROCEDURE_VERSION_PUBLISHED for item in procedure.versions
        )
    ):
        abort(404)
    versions = sorted(procedure.versions, key=lambda item: item.version, reverse=True)
    events = sorted(procedure.events, key=lambda item: item.created_at, reverse=True)
    return render_template(
        "maintenance_execution/procedure_detail.html",
        procedure=procedure,
        versions=versions,
        events=events,
        can_manage=can_manage,
        can_publish=can_publish_maintenance_procedures(current_user),
    )


@maintenance_execution_bp.route(
    "/<int:procedure_id>/versions/<int:version_id>/edit", methods=["GET", "POST"]
)
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def version_edit(procedure_id: int, version_id: int):
    version = _version_or_404(procedure_id, version_id)
    if not version.editable:
        flash("Una versión publicada o retirada es de solo lectura.", "warning")
        return redirect(
            url_for("maintenance_execution.procedure_detail", procedure_id=procedure_id)
        )
    if request.method == "POST":
        try:
            save_draft_version(
                version,
                _empresa_id(),
                current_user.id,
                request.form,
                _steps_from_form(),
            )
            db.session.commit()
            flash("Borrador guardado.", "success")
            return redirect(
                url_for("maintenance_execution.procedure_detail", procedure_id=procedure_id)
            )
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    return render_template(
        "maintenance_execution/version_form.html",
        procedure=version.procedure,
        version=version,
        response_types=PROCEDURE_RESPONSE_TYPES,
    )


@maintenance_execution_bp.route("/<int:procedure_id>/versions/new", methods=["POST"])
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def version_new(procedure_id: int):
    procedure = _procedure_or_404(procedure_id)
    try:
        version = create_draft_version(procedure, _empresa_id(), current_user.id)
        db.session.commit()
        return redirect(
            url_for(
                "maintenance_execution.version_edit",
                procedure_id=procedure_id,
                version_id=version.id,
            )
        )
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
        return redirect(
            url_for("maintenance_execution.procedure_detail", procedure_id=procedure_id)
        )


@maintenance_execution_bp.route(
    "/<int:procedure_id>/versions/<int:version_id>/publish", methods=["POST"]
)
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_publisher_required
def version_publish(procedure_id: int, version_id: int):
    version = _version_or_404(procedure_id, version_id)
    try:
        publish_version(version, _empresa_id(), current_user.id)
        db.session.commit()
        flash(f"Versión {version.version} publicada.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(
        url_for("maintenance_execution.procedure_detail", procedure_id=procedure_id)
    )


@maintenance_execution_bp.route(
    "/<int:procedure_id>/versions/<int:version_id>/retire", methods=["POST"]
)
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_publisher_required
def version_retire(procedure_id: int, version_id: int):
    version = _version_or_404(procedure_id, version_id)
    try:
        retire_version(version, _empresa_id(), current_user.id)
        db.session.commit()
        flash(f"Versión {version.version} retirada.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(
        url_for("maintenance_execution.procedure_detail", procedure_id=procedure_id)
    )


def _work_order_or_404(work_order_id: int) -> WorkOrder:
    return WorkOrder.query.filter_by(
        id=work_order_id, empresa_id=_empresa_id()
    ).first_or_404()


@maintenance_execution_bp.route("/work-orders/<int:work_order_id>/checklist")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def work_order_checklist(work_order_id: int):
    work_order = _work_order_or_404(work_order_id)
    checklist = WorkOrderChecklist.query.filter_by(
        empresa_id=_empresa_id(), work_order_id=work_order.id
    ).first()
    if checklist and not can_access_checklist(checklist, current_user):
        abort(403)
    if not checklist and not can_manage_maintenance_procedures(current_user):
        abort(404)
    responses = {}
    if checklist:
        for item in checklist.responses:
            try:
                responses[item.step_id] = json.loads(item.value_json).get("value", "")
            except (TypeError, ValueError, json.JSONDecodeError):
                responses[item.step_id] = ""
    return render_template(
        "maintenance_execution/work_order_checklist.html",
        work_order=work_order,
        checklist=checklist,
        responses=responses,
        versions=published_procedures_for_work_order(work_order) if not checklist else [],
        can_assign=can_manage_maintenance_procedures(current_user),
        can_execute=bool(checklist and can_access_checklist(checklist, current_user)),
        can_review=bool(checklist and can_manage_maintenance_procedures(current_user)),
    )


@maintenance_execution_bp.post("/work-orders/<int:work_order_id>/checklist/assign")
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def work_order_checklist_assign(work_order_id: int):
    work_order = _work_order_or_404(work_order_id)
    try:
        assign_checklist(
            work_order, request.form.get("procedure_version_id", type=int), current_user.id
        )
        db.session.commit()
        flash("Procedimiento asignado a la OT.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("maintenance_execution.work_order_checklist", work_order_id=work_order.id))


@maintenance_execution_bp.post("/work-orders/<int:work_order_id>/checklist/execute")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def work_order_checklist_execute(work_order_id: int):
    work_order = _work_order_or_404(work_order_id)
    checklist = WorkOrderChecklist.query.filter_by(
        empresa_id=_empresa_id(), work_order_id=work_order.id
    ).first_or_404()
    if not can_access_checklist(checklist, current_user):
        abort(403)
    saved_paths = []
    try:
        save_checklist_responses(checklist, current_user.id, request.form)
        for step in checklist.procedure_version.steps:
            if step.response_type != "evidence":
                continue
            for upload in request.files.getlist(f"evidence_{step.id}"):
                if not upload or not upload.filename:
                    continue
                response, _actor, _performer = response_for_evidence(
                    checklist, step, current_user.id
                )
                stored = save_evidence_file(
                    upload, checklist.empresa_id, checklist.id
                )
                saved_paths.append(stored.pop("path"))
                register_evidence_metadata(
                    response, current_user.id, **stored
                )
        db.session.commit()
        flash("Checklist completado." if checklist.status == "completed" else "Avance del checklist guardado.", "success")
    except ValueError as exc:
        db.session.rollback()
        for path in saved_paths:
            path.unlink(missing_ok=True)
        flash(str(exc), "danger")
    return redirect(url_for("maintenance_execution.work_order_checklist", work_order_id=work_order.id))


@maintenance_execution_bp.post("/work-orders/<int:work_order_id>/checklist/review")
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def work_order_checklist_review(work_order_id: int):
    work_order = _work_order_or_404(work_order_id)
    checklist = WorkOrderChecklist.query.filter_by(
        empresa_id=_empresa_id(), work_order_id=work_order.id
    ).first_or_404()
    try:
        review_checklist(checklist, current_user.id, request.form)
        db.session.commit()
        flash("Checklist revisado y aprobado.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("maintenance_execution.work_order_checklist", work_order_id=work_order.id))


@maintenance_execution_bp.get("/work-orders/<int:work_order_id>/checklist/evidence/<int:evidence_id>")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def work_order_checklist_evidence_download(work_order_id: int, evidence_id: int):
    work_order = _work_order_or_404(work_order_id)
    checklist = WorkOrderChecklist.query.filter_by(
        empresa_id=_empresa_id(), work_order_id=work_order.id
    ).first_or_404()
    if not can_access_checklist(checklist, current_user):
        abort(403)
    evidence = WorkOrderChecklistEvidence.query.filter_by(
        id=evidence_id, empresa_id=_empresa_id(), checklist_id=checklist.id
    ).first_or_404()
    try:
        path = resolve_evidence_path(evidence.storage_key)
    except ValueError:
        abort(404)
    if not path.is_file():
        abort(404)
    db.session.add(WorkOrderChecklistEvent(
        empresa_id=checklist.empresa_id,
        checklist_id=checklist.id,
        event="evidence_downloaded",
        actor_id=current_user.id,
        detail=evidence.original_name[:500],
    ))
    db.session.commit()
    return send_file(path, as_attachment=True, download_name=evidence.original_name, mimetype=evidence.mime_type)


@maintenance_execution_bp.route("/context/<entity_type>/<int:entity_id>/log", methods=["GET", "POST"])
@login_required
@require_module(MODULO_MANTENIMIENTO)
def context_log(entity_type: str, entity_id: int):
    try:
        entity = resolve_log_context(entity_type, entity_id, _empresa_id())
    except ValueError:
        abort(404)
    if not can_view_log(current_user, entity_type, entity):
        abort(403)
    saved_paths = []
    if request.method == "POST":
        try:
            entry = create_log_entry(current_user, entity_type, entity, request.form)
            for upload in request.files.getlist("attachments"):
                if not upload or not upload.filename:
                    continue
                stored = save_log_file(upload, entry.empresa_id, entry.id)
                saved_paths.append(stored.pop("path"))
                attach_log_file(entry, current_user.id, stored)
            db.session.commit()
            flash("Entrada agregada a la bitácora.", "success")
            return redirect(url_for("maintenance_execution.context_log", entity_type=entity_type, entity_id=entity.id))
        except (ValueError, TypeError) as exc:
            db.session.rollback()
            for path in saved_paths: path.unlink(missing_ok=True)
            flash(str(exc), "danger")
    if entity_type == "work_order":
        title = f"{entity.numero or ('OT-' + str(entity.id))} · {entity.titulo}"
    elif entity_type == "incident":
        title = f"{entity.numero or ('INC-' + str(entity.id))} · {entity.titulo}"
    else:
        title = f"{entity.codigo} · {entity.nombre}"
    performers = User.query.filter_by(empresa_id=_empresa_id(), activo=True).filter(User.rol.in_(["tecnico", "supervisor", "admin"])).order_by(User.nombre_visible, User.username).all()
    return render_template(
        "maintenance_execution/context_log.html", entity=entity, entity_type=entity_type,
        context_title=title, entries=entries_for_context(current_user, entity_type, entity),
        can_write=can_write_log(current_user, entity_type, entity),
        can_publish_requester=bool(current_user.rol in {"admin", "superadmin", "supervisor"} and entity_type == "incident"),
        performers=performers,
    )


@maintenance_execution_bp.get("/context/log/attachment/<int:attachment_id>")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def context_log_attachment_download(attachment_id: int):
    attachment = MaintenanceLogAttachment.query.filter_by(id=attachment_id, empresa_id=_empresa_id()).first_or_404()
    entry = attachment.entry
    entity_type = "work_order" if entry.work_order_id else "incident" if entry.incident_id else "machine"
    entity = entry.work_order or entry.incident or entry.machine
    if not can_view_log(current_user, entity_type, entity): abort(403)
    if current_user.id == getattr(entity, "user_id", None) and entry.visibility != "requester": abort(403)
    try: path = resolve_log_file(attachment.storage_key)
    except ValueError: abort(404)
    if not path.is_file(): abort(404)
    audit_log_access(entry, current_user.id, "log_attachment_downloaded", attachment.original_name)
    db.session.commit()
    return send_file(path, as_attachment=True, download_name=attachment.original_name, mimetype=attachment.mime_type)


@maintenance_execution_bp.get("/context/notifications")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def context_log_notifications():
    return render_template(
        "maintenance_execution/log_notifications.html",
        notifications=log_notifications_for_user(current_user),
    )


@maintenance_execution_bp.post("/context/notifications/<int:notification_id>/read")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def context_log_notification_read(notification_id: int):
    notification = MaintenanceLogNotification.query.filter_by(
        id=notification_id, empresa_id=_empresa_id(), user_id=current_user.id
    ).first_or_404()
    mark_log_notification_read(notification, current_user)
    entry = notification.entry
    if entry.work_order_id:
        entity_type, entity_id = "work_order", entry.work_order_id
    elif entry.incident_id:
        entity_type, entity_id = "incident", entry.incident_id
    else:
        entity_type, entity_id = "machine", entry.machine_id
    db.session.commit()
    return redirect(url_for("maintenance_execution.context_log", entity_type=entity_type, entity_id=entity_id))


def _machine_or_404(machine_id: int) -> Machine:
    return Machine.query.filter_by(id=machine_id, empresa_id=_empresa_id()).first_or_404()


@maintenance_execution_bp.route("/assets/<int:machine_id>/meters", methods=["GET", "POST"])
@login_required
@require_module(MODULO_MANTENIMIENTO)
def asset_meters(machine_id: int):
    machine = _machine_or_404(machine_id)
    if not can_view_meters(current_user, machine):
        abort(403)
    if request.method == "POST":
        if not can_manage_meters(current_user, machine):
            abort(403)
        try:
            create_meter(machine, current_user, request.form)
            db.session.commit()
            flash("Medidor creado correctamente.", "success")
            return redirect(url_for("maintenance_execution.asset_meters", machine_id=machine.id))
        except ValueError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    work_order_id = request.args.get("work_order_id", type=int)
    related_order = None
    if work_order_id:
        related_order = WorkOrder.query.filter_by(
            id=work_order_id, empresa_id=machine.empresa_id, machine_id=machine.id
        ).first()
    return render_template(
        "maintenance_execution/asset_meters.html",
        machine=machine,
        meters=meters_for_machine(machine),
        meter_types=METER_TYPES,
        can_manage=can_manage_meters(current_user, machine),
        related_order=related_order,
        performers=performers_for_meter(current_user, machine),
    )


@maintenance_execution_bp.post("/assets/<int:machine_id>/meters/<int:meter_id>/reading")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def asset_meter_reading(machine_id: int, meter_id: int):
    machine = _machine_or_404(machine_id)
    meter = AssetMeter.query.filter_by(
        id=meter_id, empresa_id=machine.empresa_id, machine_id=machine.id
    ).first_or_404()
    if not can_record_reading(current_user, meter):
        abort(403)
    try:
        record_reading(meter, current_user, request.form)
        db.session.commit()
        flash("Lectura registrada y auditada.", "success")
    except (TypeError, ValueError) as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    params = {"machine_id": machine.id}
    if request.form.get("work_order_id"):
        params["work_order_id"] = request.form.get("work_order_id")
    return redirect(url_for("maintenance_execution.asset_meters", **params))


@maintenance_execution_bp.post("/assets/<int:machine_id>/meters/<int:meter_id>/active")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def asset_meter_active(machine_id: int, meter_id: int):
    machine = _machine_or_404(machine_id)
    meter = AssetMeter.query.filter_by(
        id=meter_id, empresa_id=machine.empresa_id, machine_id=machine.id
    ).first_or_404()
    if not can_manage_meters(current_user, machine):
        abort(403)
    try:
        set_meter_active(meter, current_user, request.form.get("active") == "1")
        db.session.commit()
        flash("Estado del medidor actualizado.", "success")
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
    return redirect(url_for("maintenance_execution.asset_meters", machine_id=machine.id))
