"""Decorador de acceso por módulo activo."""

from __future__ import annotations

from functools import wraps
from typing import Callable

from flask import flash, redirect, url_for
from flask_login import current_user

from app.modules import empresa_tiene_modulo


def require_module(modulo: str):
    """Redirige al dashboard si la empresa no tiene el módulo activo."""

    def decorator(view: Callable):
        @wraps(view)
        def wrapped(*args, **kwargs):
            empresa = getattr(current_user, "empresa", None) if current_user.is_authenticated else None
            if not empresa_tiene_modulo(empresa, modulo):
                flash("Tu plan no incluye este módulo.", "warning")
                return redirect(url_for("main.dashboard"))
            return view(*args, **kwargs)

        return wrapped

    return decorator
