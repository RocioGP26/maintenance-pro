"""Middleware: JWT o sesión Flask → g.empresa_id para toda la request."""

from __future__ import annotations

import jwt
from flask import Flask, g, jsonify, redirect, request, url_for
from flask_login import current_user

from app.tenancy.db import close_db
from app.tenancy.jwt_auth import verificar_token

_PUBLIC_PREFIXES = (
    "static",
    "onboarding.",
    "platform.",
    "health.",
)
_PUBLIC_EXACT = {
    "main.index",
    "main.faq",
    "main.demo",
    "main.contacto",
    "main.recursos",
    "main.login",
    "main.logout",
    "main.cuenta_suspendida",
    "main.salir_impersonacion",
    "tenancy_api.login",
    "tenancy_api.login_v1",
    "admin.crear_empresa",
}


def _is_public_endpoint(endpoint: str) -> bool:
    if not endpoint:
        return True
    if endpoint in _PUBLIC_EXACT:
        return True
    return any(endpoint.startswith(prefix) for prefix in _PUBLIC_PREFIXES)


def _reset_tenant_context() -> None:
    g.empresa_id = None
    g.empresa_slug = None
    g.user_id = None
    g.user_rol = None


def _load_from_session_user() -> None:
    if not current_user.is_authenticated:
        return
    g.user_id = current_user.id
    g.user_rol = getattr(current_user, "rol", None)
    g.empresa_id = getattr(current_user, "empresa_id", None)
    empresa = getattr(current_user, "empresa", None)
    if empresa and getattr(empresa, "slug", None):
        g.empresa_slug = empresa.slug


def _sync_ordenes_vencidas() -> None:
    eid = getattr(g, "empresa_id", None)
    if not eid or getattr(g, "_ot_vencidas_synced", False):
        return
    from app.work_order_status import sincronizar_estados_ordenes

    sincronizar_estados_ordenes(int(eid))
    g._ot_vencidas_synced = True


def _verificar_modulo_activo(endpoint: str):
    from flask import flash, redirect, url_for

    from app.models import Empresa
    from app.modules import (
        MODULO_INVENTARIO,
        MODULO_MANTENIMIENTO,
        endpoint_exento_modulo,
        empresa_tiene_modulo,
        modulo_requerido_por_endpoint,
    )

    if endpoint_exento_modulo(endpoint):
        return None
    modulo = modulo_requerido_por_endpoint(endpoint)
    if not modulo:
        return None
    eid = getattr(g, "empresa_id", None)
    if not eid:
        return None
    empresa = Empresa.query.get(int(eid))
    if empresa_tiene_modulo(empresa, modulo):
        return None
    flash("Tu plan no incluye este módulo.", "warning")
    if empresa_tiene_modulo(empresa, MODULO_INVENTARIO):
        return redirect(url_for("inv_comercial.dashboard_inventario"))
    if empresa_tiene_modulo(empresa, MODULO_MANTENIMIENTO):
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


def _verificar_modulo_rol(endpoint: str):
    """Restringe módulos por rol aunque la empresa tenga ambos contratados."""
    from flask import flash, redirect, url_for

    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO, modulo_requerido_por_endpoint
    from app.permissions import UserRole, can_access_inventory, normalize_rol

    modulo = modulo_requerido_por_endpoint(endpoint)
    rol = normalize_rol(getattr(g, "user_rol", None))
    if rol == UserRole.VENDEDOR.value and endpoint == "main.dashboard":
        return redirect(url_for("inv_comercial.dashboard_inventario"))
    usuario = current_user if current_user.is_authenticated else None
    if usuario is None and getattr(g, "user_id", None):
        from app.models import User
        try:
            usuario = User.query.get(int(g.user_id))
        except (TypeError, ValueError):
            usuario = None
    if modulo == MODULO_INVENTARIO and usuario is not None and not can_access_inventory(usuario):
        if rol == UserRole.ADMIN.value:
            flash("Los administradores del área de Mantenimiento no tienen acceso a Inventario.", "warning")
        else:
            flash("El rol Técnico solo tiene acceso al módulo de Mantenimiento.", "warning")
        return redirect(url_for("main.dashboard"))
    if rol == UserRole.VENDEDOR.value and modulo == MODULO_MANTENIMIENTO:
        if endpoint == "main.incidencia" or endpoint.startswith("main.incidencias"):
            return None
        flash("El rol Vendedor solo tiene acceso a Inventario comercial.", "warning")
        return redirect(url_for("inv_comercial.dashboard_inventario"))
    return None


def _verificar_bloqueo_tenant(endpoint: str):
    from app.models import Empresa
    from app.tenant_activity import empresa_puede_operar, endpoint_exento_bloqueo

    if _is_public_endpoint(endpoint) or endpoint_exento_bloqueo(endpoint):
        return None
    eid = getattr(g, "empresa_id", None)
    if not eid:
        return None
    empresa = Empresa.query.get(int(eid))
    puede, codigo, mensaje = empresa_puede_operar(empresa)
    if puede:
        return None
    if request.path.startswith("/api/"):
        return jsonify({"error": mensaje, "codigo": codigo}), 403
    if endpoint == "main.cuenta_suspendida":
        return None
    return redirect(url_for("main.cuenta_suspendida", motivo=codigo))


def register_tenancy_middleware(app: Flask) -> None:
    @app.before_request
    def middleware_tenancy():
        _reset_tenant_context()
        endpoint = request.endpoint or ""

        if _is_public_endpoint(endpoint):
            return None

        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:].strip()
            if not token:
                return jsonify({"error": "Token vacío"}), 401
            try:
                payload = verificar_token(token, app.config["SECRET_KEY"])
            except jwt.ExpiredSignatureError:
                return jsonify({"error": "Token expirado"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Token inválido"}), 401

            g.user_id = payload.get("sub")
            g.empresa_id = payload.get("empresa_id")
            g.empresa_slug = payload.get("empresa_slug")
            g.user_rol = payload.get("rol")
            _sync_ordenes_vencidas()
            bloqueo = _verificar_bloqueo_tenant(endpoint)
            if bloqueo is not None:
                return bloqueo
            modulo = _verificar_modulo_activo(endpoint)
            if modulo is not None:
                return modulo
            modulo_rol = _verificar_modulo_rol(endpoint)
            if modulo_rol is not None:
                return modulo_rol
            return None

        _load_from_session_user()
        _sync_ordenes_vencidas()
        bloqueo = _verificar_bloqueo_tenant(endpoint)
        if bloqueo is not None:
            return bloqueo
        modulo = _verificar_modulo_activo(endpoint)
        if modulo is not None:
            return modulo
        modulo_rol = _verificar_modulo_rol(endpoint)
        if modulo_rol is not None:
            return modulo_rol
        return None

    @app.teardown_appcontext
    def _teardown_tenant_db(exception):
        close_db(exception)
