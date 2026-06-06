"""Consultas siempre acotadas por empresa_id."""

from __future__ import annotations

from typing import Type, TypeVar

from app.tenancy.context import current_empresa_id
from app.tenancy.db import get_db

T = TypeVar("T")


def query_tenant(model: Type[T]):
    """SELECT con filtro empresa_id automático."""
    eid = current_empresa_id()
    if eid is None:
        raise RuntimeError("No hay contexto de tenant.")
    session = get_db()
    q = session.query(model)
    if hasattr(model, "empresa_id"):
        q = q.filter(model.empresa_id == eid)
    return q


def insertar_tenant(instance) -> object:
    """INSERT con empresa_id del tenant activo."""
    eid = current_empresa_id()
    if eid is None:
        raise RuntimeError("No hay contexto de tenant.")
    if hasattr(instance, "empresa_id"):
        instance.empresa_id = eid
    session = get_db()
    session.add(instance)
    session.commit()
    return instance


def verificar_pertenencia(instance) -> bool:
    """Comprueba que un registro pertenece al tenant de la request."""
    if instance is None:
        return False
    eid = current_empresa_id()
    if eid is None:
        return False
    if hasattr(instance, "empresa_id"):
        record_eid = getattr(instance, "empresa_id", None)
        if record_eid is not None and int(record_eid) != int(eid):
            return False
    return True


def get_tenant_or_404(model: Type[T], id: int) -> T:
    """Obtiene un registro por id acotado al tenant activo."""
    from flask import abort

    row = query_tenant(model).filter(model.id == id).first()
    if row is None:
        abort(404)
    return row

