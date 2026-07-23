"""Gestión centralizada de sesiones web: expiración, revocación y auditoría."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

from flask import flash, jsonify, redirect, request, session, url_for
from flask_login import current_user, logout_user

from app import db
from app.models import ActiveSession, User

SESSION_KEY = "managed_session_key"
LAST_TOUCH_KEY = "managed_session_touch"

PUBLIC_ENDPOINTS = {
    "main.index",
    "main.login",
    "main.faq",
    "main.demo",
    "main.contacto",
    "main.recursos",
    "main.guia_producto",
    "onboarding.wizard",
    "onboarding.verify_email",
    "static",
}


def _utcnow() -> datetime:
    return datetime.utcnow()


def _client_ip() -> str:
    forwarded = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    return (forwarded or request.remote_addr or "")[:45]


def policy_for(user: User) -> dict[str, int | bool]:
    empresa = user.empresa
    return {
        "idle_minutes": int(getattr(empresa, "session_idle_minutes", 30) or 30),
        "absolute_minutes": int(getattr(empresa, "session_absolute_minutes", 480) or 480),
        "remember_enabled": bool(getattr(empresa, "session_remember_enabled", False)),
        "warning_enabled": bool(getattr(empresa, "session_warning_enabled", True)),
        "warning_minutes": int(getattr(empresa, "session_warning_minutes", 2) or 2),
        "revoke_on_password": bool(getattr(empresa, "session_revoke_on_password", True)),
        "allow_multiple": bool(getattr(empresa, "session_allow_multiple", True)),
    }


def start_managed_session(user: User, *, remember: bool = False) -> ActiveSession:
    """Crea el registro servidor y enlaza la cookie firmada a él."""
    now = _utcnow()
    policy = policy_for(user)
    remember = bool(remember and policy["remember_enabled"])
    if not policy["allow_multiple"]:
        revoke_user_sessions(user.id, reason="nuevo_login", except_key=None)
    item = ActiveSession(
        session_key=str(uuid4()),
        empresa_id=user.empresa_id,
        user_id=user.id,
        started_at=now,
        last_activity_at=now,
        absolute_expires_at=now + timedelta(minutes=int(policy["absolute_minutes"])),
        ip_address=_client_ip(),
        user_agent=(request.headers.get("User-Agent") or "")[:500],
        remember=remember,
    )
    db.session.add(item)
    db.session.flush()
    session[SESSION_KEY] = item.session_key
    session[LAST_TOUCH_KEY] = int(now.timestamp())
    session.permanent = remember
    return item


def current_managed_session() -> ActiveSession | None:
    key = session.get(SESSION_KEY)
    if not key:
        return None
    return ActiveSession.query.filter_by(session_key=key).first()


def revoke_session(item: ActiveSession | None, *, reason: str) -> None:
    if item is not None and item.revoked_at is None:
        item.revoked_at = _utcnow()
        item.revoked_reason = (reason or "revocada")[:80]


def revoke_user_sessions(user_id: int, *, reason: str, except_key: str | None = None) -> int:
    query = ActiveSession.query.filter_by(user_id=user_id, revoked_at=None)
    if except_key:
        query = query.filter(ActiveSession.session_key != except_key)
    now = _utcnow()
    return query.update(
        {ActiveSession.revoked_at: now, ActiveSession.revoked_reason: reason[:80]},
        synchronize_session=False,
    )


def revoke_company_sessions(empresa_id: int, *, reason: str) -> int:
    now = _utcnow()
    count = (
        ActiveSession.query.filter_by(empresa_id=empresa_id, revoked_at=None)
        .update(
            {ActiveSession.revoked_at: now, ActiveSession.revoked_reason: reason[:80]},
            synchronize_session=False,
        )
    )
    User.query.filter_by(empresa_id=empresa_id).update(
        {User.auth_version: User.auth_version + 1}, synchronize_session=False
    )
    return count


def _audit_expiration(item: ActiveSession, reason: str) -> None:
    if not item.empresa_id:
        return
    from app.tenant_activity import registrar_actividad_tenant

    registrar_actividad_tenant(
        item.empresa_id,
        "session_expired",
        user_id=item.user_id,
        username=item.user.username if item.user else "",
        detalle="Expiración por inactividad" if reason == "idle_timeout" else "Tiempo máximo alcanzado",
    )


def _expire(item: ActiveSession, reason: str):
    revoke_session(item, reason=reason)
    _audit_expiration(item, reason)
    db.session.commit()
    logout_user()
    session.clear()
    if request.endpoint == "main.session_status":
        return jsonify({"authenticated": False, "reason": reason}), 401
    flash("Tu sesión expiró por seguridad. Inicia sesión nuevamente.", "warning")
    return redirect(url_for("main.login", expired=reason))


def register_session_management(app) -> None:
    @app.before_request
    def _enforce_managed_session():
        endpoint = request.endpoint or ""
        if endpoint in PUBLIC_ENDPOINTS or endpoint.startswith(("health.", "onboarding.")):
            return None
        if not current_user.is_authenticated:
            # La cookie contenía una identidad que ya no es válida (versión cambiada,
            # usuario bloqueado/eliminado). Limpia también el contexto tenant.
            if session.get("_user_id") or session.get(SESSION_KEY):
                item = current_managed_session()
                revoke_session(item, reason="identity_invalidated")
                db.session.commit()
                session.clear()
                return redirect(url_for("main.login", expired="revoked"))
            return None

        item = current_managed_session()
        # Compatibilidad con sesiones de onboarding, impersonación o cookies remember previas.
        if item is None:
            restored = session.get("_fresh") is False
            item = start_managed_session(user=current_user, remember=restored)
            if restored and current_user.empresa_id:
                from app.tenant_activity import registrar_actividad_tenant

                registrar_actividad_tenant(
                    current_user.empresa_id,
                    "session_reauthenticated",
                    user_id=current_user.id,
                    username=current_user.username,
                    detalle="Sesión restaurada mediante Recordarme",
                )

        now = _utcnow()
        if item.user_id != current_user.id or item.revoked_at is not None:
            return _expire(item, "revoked")
        policy = policy_for(current_user)
        if now >= item.absolute_expires_at:
            return _expire(item, "absolute_timeout")
        if now - item.last_activity_at >= timedelta(minutes=int(policy["idle_minutes"])):
            return _expire(item, "idle_timeout")

        # Evita una escritura por cada recurso/petición; el ping explícito fuerza actualización.
        force = endpoint == "main.session_status" and request.method == "POST"
        last_touch = int(session.get(LAST_TOUCH_KEY) or 0)
        if force or int(now.timestamp()) - last_touch >= 60:
            item.last_activity_at = now
            session[LAST_TOUCH_KEY] = int(now.timestamp())
        return None


def session_payload(item: ActiveSession, user: User) -> dict:
    now = _utcnow()
    policy = policy_for(user)
    idle_expires = item.last_activity_at + timedelta(minutes=int(policy["idle_minutes"]))
    expires = min(idle_expires, item.absolute_expires_at)
    return {
        "authenticated": True,
        "seconds_remaining": max(0, int((expires - now).total_seconds())),
        "warning_seconds": int(policy["warning_minutes"]) * 60,
        "warning_enabled": bool(policy["warning_enabled"]),
        "absolute_expires_at": item.absolute_expires_at.isoformat() + "Z",
    }


def describe_user_agent(value: str) -> tuple[str, str]:
    raw = value or ""
    browser = next((x for x in ("Edge", "Chrome", "Firefox", "Safari") if x.lower() in raw.lower()), "Navegador")
    if "Edg/" in raw:
        browser = "Edge"
    system = next((x for x in ("Windows", "Android", "iPhone", "iPad", "Mac", "Linux") if x.lower() in raw.lower()), "Dispositivo")
    return browser, system
