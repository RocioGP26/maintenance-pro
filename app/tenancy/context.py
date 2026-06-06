"""Contexto de tenant compartido: web (sesión) y API (JWT)."""

from __future__ import annotations

from typing import Optional

from flask import g
from flask_login import current_user


def current_empresa_id() -> Optional[int]:
    """empresa_id activo: primero g (middleware JWT/sesión), luego current_user."""
    eid = getattr(g, "empresa_id", None)
    if eid is not None:
        return int(eid)
    if current_user.is_authenticated and current_user.empresa_id:
        return int(current_user.empresa_id)
    return None
