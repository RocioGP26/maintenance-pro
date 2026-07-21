"""Vistas de Asset Health avanzado."""

from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.asset_health.models import AssetHealthSnapshot
from app.asset_health.service import BAND_META, calculate_asset_health, portfolio_health, refresh_tenant_health
from app.maintenance_execution.meter_service import technician_related_to_machine
from app.models import Machine
from app.module_guard import require_module
from app.modules import MODULO_MANTENIMIENTO


asset_health_bp = Blueprint("asset_health", __name__, url_prefix="/maintenance/asset-health")
MANAGER_ROLES = {"admin", "superadmin", "supervisor"}


def _manager() -> bool:
    return (getattr(current_user, "rol", "") or "").strip().lower() in MANAGER_ROLES


def _empresa_id() -> int:
    value = getattr(current_user, "empresa_id", None)
    if value is None:
        abort(403)
    return int(value)


def _can_view(machine: Machine) -> bool:
    return machine.empresa_id == _empresa_id() and (
        _manager() or technician_related_to_machine(current_user, machine)
    )


@asset_health_bp.get("/")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def portfolio():
    machines = Machine.query.filter_by(empresa_id=_empresa_id()).order_by(Machine.nombre).all()
    if not _manager():
        machines = [machine for machine in machines if technician_related_to_machine(current_user, machine)]
    data = portfolio_health(machines)
    band = (request.args.get("band") or "").strip().lower()
    criticality = (request.args.get("criticality") or "").strip().lower()
    query = (request.args.get("q") or "").strip().lower()
    items = data["items"]
    if band == "attention":
        items = [item for item in items if item["band"] in {"at_risk", "critical"}]
    elif band in BAND_META:
        items = [item for item in items if item["band"] == band]
    if criticality:
        items = [item for item in items if (item["machine"].criticidad or "").lower() == criticality]
    if query:
        items = [item for item in items if query in f"{item['machine'].codigo} {item['machine'].nombre} {item['machine'].ubicacion}".lower()]
    return render_template(
        "asset_health/portfolio.html", health=data, items=items, band_meta=BAND_META,
        band_filter=band, criticality_filter=criticality, q=query, can_refresh=_manager(),
    )


@asset_health_bp.get("/assets/<int:machine_id>")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def detail(machine_id: int):
    machine = Machine.query.filter_by(id=machine_id, empresa_id=_empresa_id()).first_or_404()
    if not _can_view(machine):
        abort(403)
    current = calculate_asset_health(machine)
    history = AssetHealthSnapshot.query.filter_by(
        empresa_id=_empresa_id(), machine_id=machine.id
    ).order_by(AssetHealthSnapshot.calculated_at.desc()).limit(30).all()
    return render_template(
        "asset_health/detail.html", machine=machine, health=current,
        history=history, band_meta=BAND_META, can_refresh=_manager(),
    )


@asset_health_bp.post("/refresh")
@login_required
@require_module(MODULO_MANTENIMIENTO)
def refresh():
    if not _manager():
        abort(403)
    created = refresh_tenant_health(
        _empresa_id(), trigger="manual_refresh", actor_id=current_user.id
    )
    db.session.commit()
    flash(f"Asset Health actualizado. {created} snapshot(s) nuevo(s).", "success")
    machine_id = request.form.get("machine_id", type=int)
    if machine_id:
        return redirect(url_for("asset_health.detail", machine_id=machine_id))
    return redirect(url_for("asset_health.portfolio"))
