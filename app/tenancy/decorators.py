"""@tenant_required y @rol_required."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import g, jsonify, request

from app.tenancy.context import current_empresa_id


def tenant_required(view: Callable):
    """Garantiza que hay empresa_id en el contexto (JWT o sesión)."""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_empresa_id() is None:
            if request.path.startswith("/api/v1"):
                from app.public_api.contract import api_error

                return api_error("TENANT_REQUIRED", "Contexto de empresa requerido.", 403)
            return jsonify({"error": "Contexto de empresa requerido"}), 403
        return view(*args, **kwargs)

    return wrapped


def rol_required(*roles: str):
    """Restringe el endpoint a uno o más roles."""

    def decorator(view: Callable):
        @wraps(view)
        def wrapped(*args, **kwargs):
            rol = (getattr(g, "user_rol", None) or "").strip().lower()
            permitidos = {r.strip().lower() for r in roles}
            if rol not in permitidos:
                if request.path.startswith("/api/v1"):
                    from app.public_api.contract import api_error

                    return api_error("PERMISSION_DENIED", "Sin permiso para esta acción.", 403)
                return jsonify({"error": "Sin permiso para esta acción"}), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator
