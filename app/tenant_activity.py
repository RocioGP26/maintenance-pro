"""Registro de actividad y acceso operativo de tenants."""

from __future__ import annotations

from typing import Optional

from flask import request, session

from app import db
from app.models import Empresa, TenantActivityLog
from app.platform_service import estado_ciclo_empresa

ACTIVITY_LABELS = {
    "login": "Inicio de sesión",
    "logout": "Cierre de sesión",
    "impersonate_start": "Impersonación (soporte)",
    "impersonate_end": "Fin impersonación",
    "factura_pagada": "Pago registrado",
    "acceso_bloqueado": "Acceso bloqueado",
}


def _client_ip() -> str:
    forwarded = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    return forwarded or (request.remote_addr or "")


def registrar_actividad_tenant(
    empresa_id: int,
    tipo: str,
    *,
    user_id: Optional[int] = None,
    username: str = "",
    detalle: str = "",
) -> None:
    db.session.add(
        TenantActivityLog(
            empresa_id=empresa_id,
            user_id=user_id,
            username=(username or "")[:80],
            tipo=tipo,
            detalle=(detalle or "")[:500],
            ip_address=_client_ip(),
        )
    )


def ultima_actividad_empresa(empresa_id: int, limit: int = 25) -> list[TenantActivityLog]:
    return (
        TenantActivityLog.query.filter_by(empresa_id=empresa_id)
        .order_by(TenantActivityLog.created_at.desc())
        .limit(limit)
        .all()
    )


def empresa_puede_operar(empresa: Empresa | None) -> tuple[bool, str, str]:
    """
    Devuelve (puede_operar, codigo, mensaje).
    Bloquea suspendidas y en mora (excepto impersonación de soporte).
    """
    if empresa is None:
        return True, "", ""
    if session.get("platform_impersonating"):
        return True, "", ""
    if empresa.suspendida:
        return (
            False,
            "suspendida",
            "Esta cuenta está suspendida. Contacta a soporte de Maintix para reactivarla.",
        )
    estado = estado_ciclo_empresa(empresa)
    if estado == "suspendida":
        return (
            False,
            "suspendida",
            "El periodo de prueba o suscripción de esta cuenta ha finalizado.",
        )
    if estado == "mora":
        return (
            False,
            "mora",
            "Hay pagos pendientes. Regulariza la facturación para continuar usando Maintix.",
        )
    return True, "", ""


def endpoint_exento_bloqueo(endpoint: str) -> bool:
    return endpoint in {
        "main.login",
        "main.logout",
        "main.salir_impersonacion",
        "main.cuenta_suspendida",
    }
