"""Autorización por scopes para identidades técnicas."""

from __future__ import annotations

from functools import wraps

from flask import g, jsonify, request


def scope_required(scope: str):
    """Exige un scope solo cuando el actor es una API key.

    Los JWT de usuario conservan el contrato de roles existente. Las rutas
    administrativas deben seguir usando ``rol_required``.
    """

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if getattr(g, "auth_type", None) == "api_key":
                scopes = set(getattr(g, "api_scopes", ()) or ())
                if scope not in scopes:
                    if request.path.startswith("/api/v1"):
                        from app.public_api.contract import api_error

                        return api_error(
                            "SCOPE_REQUIRED",
                            "La credencial no permite esta operación.",
                            403,
                            details={"required_scope": scope},
                        )
                    return jsonify(
                        {
                            "error": "Scope insuficiente",
                            "codigo": "insufficient_scope",
                            "required_scope": scope,
                        }
                    ), 403
            return view(*args, **kwargs)

        return wrapped

    return decorator
