"""Auditoría obligatoria de acciones del panel de plataforma."""

from __future__ import annotations

from typing import Optional

from flask import request, session

from app import db
from app.models import PlatformAuditLog

PLATFORM_AUDIT_LABELS = {
    "impersonate_start": "Impersonación de usuario",
    "impersonate_end": "Fin de impersonación",
    "reset_password": "Contraseña restablecida",
    "block_user": "Usuario bloqueado",
    "unblock_user": "Usuario desbloqueado",
}

DEFAULT_ACTOR = "Soporte Roustix (Plataforma)"


def _client_ip() -> str:
    forwarded = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    return forwarded or (request.remote_addr or "")


def actor_plataforma() -> str:
    return (session.get("platform_actor") or DEFAULT_ACTOR).strip() or DEFAULT_ACTOR


def registrar_auditoria_plataforma(
    accion: str,
    *,
    empresa_id: Optional[int] = None,
    user_id: Optional[int] = None,
    detalle: str = "",
    visible_cliente: bool = True,
) -> PlatformAuditLog:
    log = PlatformAuditLog(
        empresa_id=empresa_id,
        user_id=user_id,
        accion=accion,
        actor_label=actor_plataforma(),
        detalle=(detalle or "")[:500],
        ip_address=_client_ip(),
        visible_cliente=visible_cliente,
    )
    db.session.add(log)
    db.session.flush()
    return log


def auditoria_visible_empresa(empresa_id: int, limit: int = 15) -> list[PlatformAuditLog]:
    return (
        PlatformAuditLog.query.filter_by(empresa_id=empresa_id, visible_cliente=True)
        .order_by(PlatformAuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
