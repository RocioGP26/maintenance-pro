"""Middleware: JWT o sesión Flask → g.empresa_id para toda la request."""

from __future__ import annotations

import jwt
from flask import Flask, g, jsonify, request
from flask_login import current_user

from app.tenancy.db import close_db
from app.tenancy.jwt_auth import verificar_token

_PUBLIC_PREFIXES = (
    "static",
    "onboarding.",
)
_PUBLIC_EXACT = {
    "main.login",
    "main.logout",
    "tenancy_api.login",
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
            return None

        _load_from_session_user()
        return None

    @app.teardown_appcontext
    def _teardown_tenant_db(exception):
        close_db(exception)
