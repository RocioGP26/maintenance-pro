"""Administración web y REST de credenciales de integración."""

from __future__ import annotations

from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db, limiter
from app.integrations.credentials import (
    ENVIRONMENTS,
    SCOPES,
    CredentialError,
    issue_credential,
    revoke_credential,
    rotate_credential,
)
from app.public_api.contract import PUBLIC_API_LIMIT, api_rate_key, success
from app.models import IntegrationCredential, WebhookDelivery, WebhookEndpoint
from app.permissions import can_manage_integrations
from app.tenant_activity import registrar_actividad_tenant
from app.integrations.webhooks import (
    WebhookError,
    create_endpoint,
    delivery_stats,
    process_pending_deliveries,
    retry_delivery,
    rotate_endpoint_secret,
    serialize_delivery,
    serialize_endpoint,
    set_endpoint_status,
)


integrations_bp = Blueprint("integrations", __name__)


def _admin_empresa_id() -> int | None:
    """Solo Superadmin o Admin de área TI/TIC/Sistemas."""
    if not current_user.is_authenticated or not can_manage_integrations(current_user):
        return None
    return int(current_user.empresa_id) if current_user.empresa_id else None


def _audit(tipo: str, item: IntegrationCredential, detail: str = "") -> None:
    registrar_actividad_tenant(
        item.empresa_id,
        tipo,
        user_id=current_user.id,
        username=current_user.username,
        detalle=detail or f"{item.name} ({item.key_prefix})",
    )


def _serialize(item: IntegrationCredential) -> dict:
    return {
        "credential_id": item.id,
        "name": item.name,
        "key_prefix": item.key_prefix,
        "environment": item.environment,
        "scopes": item.scopes,
        "active": item.active,
        "expires_at": item.expires_at.isoformat() + "Z" if item.expires_at else None,
        "last_used_at": item.last_used_at.isoformat() + "Z" if item.last_used_at else None,
        "revoked_at": item.revoked_at.isoformat() + "Z" if item.revoked_at else None,
        "created_at": item.created_at.isoformat() + "Z" if item.created_at else None,
    }


def _tenant_item(credential_id: int, empresa_id: int) -> IntegrationCredential:
    return IntegrationCredential.query.filter_by(id=credential_id, empresa_id=empresa_id).first_or_404()


def _payload() -> dict:
    return request.get_json(silent=True) or request.form.to_dict(flat=False)


def _value(data: dict, key: str, default=None):
    value = data.get(key, default)
    if isinstance(value, list) and key != "scopes":
        return value[0] if value else default
    return value


@integrations_bp.route("/administracion/integraciones/credenciales", methods=["GET", "POST"])
@login_required
def credentials_page():
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        flash(
            "Solo el área de Sistemas / TIC puede gestionar credenciales API e integraciones.",
            "warning",
        )
        return redirect(url_for("main.dashboard"))
    revealed_secret = None
    if request.method == "POST":
        try:
            issued = issue_credential(
                empresa_id=empresa_id,
                name=request.form.get("name", ""),
                environment=request.form.get("environment", "test"),
                scopes=request.form.getlist("scopes"),
                expires_at=request.form.get("expires_at") or None,
                created_by_id=current_user.id,
            )
            _audit("integration_credential_created", issued.credential)
            db.session.commit()
            revealed_secret = issued.secret
            flash("Credencial creada. Copia el secreto ahora; no volverá a mostrarse.", "success")
        except CredentialError as exc:
            db.session.rollback()
            flash(str(exc), "danger")
    items = IntegrationCredential.query.filter_by(empresa_id=empresa_id).order_by(
        IntegrationCredential.created_at.desc()
    ).all()
    return render_template(
        "configuracion/integration_credentials.html",
        credentials=items,
        scopes=SCOPES,
        environments=ENVIRONMENTS,
        revealed_secret=revealed_secret,
    )


@integrations_bp.post("/administracion/integraciones/credenciales/<int:credential_id>/revocar")
@login_required
def credential_revoke_page(credential_id: int):
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        flash("Sin permiso para revocar credenciales.", "warning")
        return redirect(url_for("main.dashboard"))
    item = _tenant_item(credential_id, empresa_id)
    if revoke_credential(item):
        _audit("integration_credential_revoked", item)
        db.session.commit()
        flash("Credencial revocada inmediatamente.", "success")
    else:
        flash("La credencial ya estaba revocada.", "info")
    return redirect(url_for("integrations.credentials_page"))


@integrations_bp.post("/administracion/integraciones/credenciales/<int:credential_id>/rotar")
@login_required
def credential_rotate_page(credential_id: int):
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        flash("Sin permiso para rotar credenciales.", "warning")
        return redirect(url_for("main.dashboard"))
    item = _tenant_item(credential_id, empresa_id)
    try:
        issued = rotate_credential(
            item,
            created_by_id=current_user.id,
            grace_minutes=request.form.get("grace_minutes", 10, type=int),
        )
        _audit("integration_credential_rotated", item, f"{item.key_prefix} → {issued.credential.key_prefix}")
        db.session.commit()
    except CredentialError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
        return redirect(url_for("integrations.credentials_page"))
    items = IntegrationCredential.query.filter_by(empresa_id=empresa_id).order_by(
        IntegrationCredential.created_at.desc()
    ).all()
    flash("Credencial rotada. Copia el nuevo secreto ahora.", "success")
    return render_template(
        "configuracion/integration_credentials.html",
        credentials=items,
        scopes=SCOPES,
        environments=ENVIRONMENTS,
        revealed_secret=issued.secret,
    )


@integrations_bp.route("/api/v1/admin/integration-credentials", methods=["GET", "POST"])
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def credentials_api():
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    if request.method == "GET":
        items = IntegrationCredential.query.filter_by(empresa_id=empresa_id).order_by(
            IntegrationCredential.created_at.desc()
        ).all()
        return jsonify({"data": [_serialize(item) for item in items]})
    data = request.get_json(silent=True) or {}
    try:
        issued = issue_credential(
            empresa_id=empresa_id,
            name=_value(data, "name", ""),
            environment=_value(data, "environment", "test"),
            scopes=_value(data, "scopes", []),
            expires_at=_value(data, "expires_at"),
            created_by_id=current_user.id,
        )
        _audit("integration_credential_created", issued.credential)
        db.session.commit()
    except CredentialError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc), "codigo": "validation_error"}), 400
    response = _serialize(issued.credential)
    response["secret"] = issued.secret
    return jsonify({"data": response}), 201


@integrations_bp.post("/api/v1/admin/integration-credentials/<int:credential_id>/revoke")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def credential_revoke_api(credential_id: int):
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    item = _tenant_item(credential_id, empresa_id)
    changed = revoke_credential(item)
    if changed:
        _audit("integration_credential_revoked", item)
        db.session.commit()
    return jsonify({"data": _serialize(item)})


    response = _serialize(issued.credential)
    response["secret"] = issued.secret
    return jsonify({"data": response}), 201


def _tenant_endpoint(endpoint_id: int, empresa_id: int) -> WebhookEndpoint:
    return WebhookEndpoint.query.filter_by(id=endpoint_id, empresa_id=empresa_id).first_or_404()


def _audit_webhook(tipo: str, item: WebhookEndpoint, detail: str = "") -> None:
    registrar_actividad_tenant(
        item.empresa_id,
        tipo,
        user_id=current_user.id,
        username=current_user.username,
        detalle=detail or f"{item.name} ({item.url})",
    )


@integrations_bp.route("/api/v1/admin/webhooks", methods=["GET", "POST"])
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhooks_api():
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    if request.method == "GET":
        items = (
            WebhookEndpoint.query.filter_by(empresa_id=empresa_id)
            .order_by(WebhookEndpoint.created_at.desc())
            .all()
        )
        return success([serialize_endpoint(item) for item in items])
    data = request.get_json(silent=True) or {}
    try:
        item, secret = create_endpoint(
            empresa_id=empresa_id,
            name=data.get("name", ""),
            url=data.get("url", ""),
            events=data.get("events", []),
            environment=data.get("environment", "test"),
            created_by_id=current_user.id,
        )
        _audit_webhook("webhook_endpoint_created", item)
        db.session.commit()
    except WebhookError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc), "codigo": "validation_error"}), 400
    payload = serialize_endpoint(item)
    payload["secret"] = secret
    return success(payload, status=201)


@integrations_bp.post("/api/v1/admin/webhooks/<int:endpoint_id>/rotate")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhook_rotate_api(endpoint_id: int):
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    item = _tenant_endpoint(endpoint_id, empresa_id)
    secret = rotate_endpoint_secret(item)
    _audit_webhook("webhook_endpoint_rotated", item)
    db.session.commit()
    payload = serialize_endpoint(item)
    payload["secret"] = secret
    return success(payload)


@integrations_bp.post("/api/v1/admin/webhooks/<int:endpoint_id>/status")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhook_status_api(endpoint_id: int):
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    item = _tenant_endpoint(endpoint_id, empresa_id)
    data = request.get_json(silent=True) or {}
    try:
        set_endpoint_status(item, data.get("status", ""))
        _audit_webhook("webhook_endpoint_status", item, f"status={item.status}")
        db.session.commit()
    except WebhookError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc), "codigo": "validation_error"}), 400
    return success(serialize_endpoint(item))


@integrations_bp.get("/api/v1/admin/webhook-deliveries")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhook_deliveries_api():
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    query = WebhookDelivery.query.filter_by(empresa_id=empresa_id).order_by(
        WebhookDelivery.created_at.desc()
    )
    endpoint_id = request.args.get("endpoint_id", type=int)
    if endpoint_id:
        query = query.filter_by(endpoint_id=endpoint_id)
    status = (request.args.get("status") or "").strip()
    if status:
        query = query.filter_by(status=status)
    items = query.limit(100).all()
    return success([serialize_delivery(item) for item in items])


@integrations_bp.get("/api/v1/admin/webhook-stats")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhook_stats_api():
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    from app.integrations.entitlements import entitlements_for_empresa

    payload = delivery_stats(empresa_id)
    payload["entitlements"] = {
        key: value
        for key, value in entitlements_for_empresa(empresa_id).items()
        if key.startswith(("webhooks.", "public_api."))
    }
    return success(payload)


INTEGRATION_AUDIT_TYPES = (
    "integration_credential_created",
    "integration_credential_revoked",
    "integration_credential_rotated",
    "webhook_endpoint_created",
    "webhook_endpoint_rotated",
    "webhook_endpoint_status",
    "webhook_endpoint_auto_disabled",
)


@integrations_bp.get("/api/v1/admin/integration-audit")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def integration_audit_api():
    """Historial de auditoría de credenciales y webhooks del tenant."""
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    from app.models import TenantActivityLog

    limit = min(max(request.args.get("limit", 50, type=int) or 50, 1), 200)
    rows = (
        TenantActivityLog.query.filter(
            TenantActivityLog.empresa_id == empresa_id,
            TenantActivityLog.tipo.in_(INTEGRATION_AUDIT_TYPES),
        )
        .order_by(TenantActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )
    data = [
        {
            "id": row.id,
            "tipo": row.tipo,
            "username": row.username,
            "detalle": row.detalle,
            "created_at": row.created_at.isoformat() + "Z" if row.created_at else None,
        }
        for row in rows
    ]
    return success(data)


@integrations_bp.post("/api/v1/admin/webhook-deliveries/<int:delivery_id>/retry")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhook_delivery_retry_api(delivery_id: int):
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    delivery = WebhookDelivery.query.filter_by(
        id=delivery_id, empresa_id=empresa_id
    ).first_or_404()
    try:
        queued = retry_delivery(delivery)
        db.session.commit()
    except WebhookError as exc:
        db.session.rollback()
        return jsonify({"error": str(exc), "codigo": "validation_error"}), 400
    return success(serialize_delivery(queued), status=201)


@integrations_bp.post("/api/v1/admin/webhooks/dispatch")
@limiter.limit(PUBLIC_API_LIMIT, key_func=api_rate_key)
def webhook_dispatch_api():
    empresa_id = _admin_empresa_id()
    if empresa_id is None:
        return jsonify({"error": "Sesión administrativa requerida"}), 403
    stats = process_pending_deliveries(limit=50)
    return success(stats)
