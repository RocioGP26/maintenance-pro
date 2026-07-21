"""UI de reglas, ejecuciones y avisos de automatización."""

from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app import db
from app.maintenance_automation.models import (
    MaintenanceAutomationNotification,
    MaintenanceAutomationRule,
)
from app.maintenance_automation.service import (
    OPERATORS,
    can_manage_automations,
    create_rule,
    mark_automation_notification_read,
    rules_for_tenant,
    set_rule_active,
    unread_automation_notifications,
)
from app.maintenance_execution.models import AssetMeter
from app.models import Technician
from app.module_guard import require_module
from app.modules import MODULO_MANTENIMIENTO


maintenance_automation_bp = Blueprint(
    "maintenance_automation", __name__, url_prefix="/maintenance/automation"
)


def _empresa_id():
    value = getattr(current_user, "empresa_id", None)
    if value is None:
        abort(403)
    return int(value)


def _manager_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not can_manage_automations(current_user):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def _rule_or_404(rule_id):
    return MaintenanceAutomationRule.query.options(
        joinedload(MaintenanceAutomationRule.meter).joinedload(AssetMeter.machine)
    ).filter_by(id=rule_id, empresa_id=_empresa_id()).first_or_404()


@maintenance_automation_bp.get("/")
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def rules_list():
    return render_template(
        "maintenance_automation/rules_list.html",
        rules=rules_for_tenant(_empresa_id()), operators=OPERATORS,
    )


@maintenance_automation_bp.route("/new", methods=["GET", "POST"])
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def rule_new():
    if request.method == "POST":
        try:
            rule = create_rule(_empresa_id(), current_user, request.form)
            db.session.commit()
            flash("Automatización creada y activada.", "success")
            return redirect(url_for("maintenance_automation.rule_detail", rule_id=rule.id))
        except (TypeError, ValueError) as exc:
            db.session.rollback(); flash(str(exc), "danger")
    meters = AssetMeter.query.options(joinedload(AssetMeter.machine)).filter_by(
        empresa_id=_empresa_id(), active=True
    ).order_by(AssetMeter.machine_id, AssetMeter.name).all()
    technicians = Technician.query.filter_by(
        empresa_id=_empresa_id(), activo=True
    ).order_by(Technician.nombre).all()
    return render_template(
        "maintenance_automation/rule_form.html", meters=meters, technicians=technicians,
        operators=OPERATORS,
    )


@maintenance_automation_bp.get("/<int:rule_id>")
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def rule_detail(rule_id):
    return render_template("maintenance_automation/rule_detail.html", rule=_rule_or_404(rule_id), operators=OPERATORS)


@maintenance_automation_bp.post("/<int:rule_id>/active")
@login_required
@require_module(MODULO_MANTENIMIENTO)
@_manager_required
def rule_active(rule_id):
    rule = _rule_or_404(rule_id)
    try:
        set_rule_active(rule, current_user, request.form.get("active") == "1")
        db.session.commit(); flash("Estado de la automatización actualizado.", "success")
    except ValueError as exc:
        db.session.rollback(); flash(str(exc), "danger")
    return redirect(url_for("maintenance_automation.rule_detail", rule_id=rule.id))


@maintenance_automation_bp.get("/notifications")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def notifications():
    items = MaintenanceAutomationNotification.query.filter_by(
        empresa_id=_empresa_id(), user_id=current_user.id
    ).order_by(MaintenanceAutomationNotification.created_at.desc()).limit(100).all()
    return render_template("maintenance_automation/notifications.html", notifications=items)


@maintenance_automation_bp.post("/notifications/<int:notification_id>/read")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def notification_read(notification_id):
    item = MaintenanceAutomationNotification.query.filter_by(
        id=notification_id, empresa_id=_empresa_id(), user_id=current_user.id
    ).first_or_404()
    try:
        mark_automation_notification_read(item, current_user); db.session.commit()
    except ValueError as exc:
        db.session.rollback(); flash(str(exc), "danger")
    if item.execution.work_order_id:
        return redirect(url_for("main.ordenes_edit", id=item.execution.work_order_id))
    return redirect(url_for("maintenance_automation.notifications"))
