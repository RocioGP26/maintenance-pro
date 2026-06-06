"""Sesión única mantenimiento.db — aislamiento por empresa_id."""

from __future__ import annotations

from flask import g

from app import db
from app.tenancy.context import current_empresa_id


def get_db():
    """
    Sesión SQLAlchemy compartida (mantenimiento.db).
    Requiere contexto de tenant vía middleware (g.empresa_id).
    """
    if current_empresa_id() is None:
        raise RuntimeError("No hay contexto de tenant (g.empresa_id).")
    return db.session


def close_db(exception=None) -> None:
    """No-op: Flask-SQLAlchemy gestiona el ciclo de vida de la sesión."""
    del exception
    g.pop("_tenant_db", None)
