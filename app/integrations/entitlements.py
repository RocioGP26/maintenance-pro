"""Derechos técnicos (entitlements) por plan · Sprint 22.4.

No se codifica `if plan == enterprise` en las rutas: se resuelve un catálogo
de capacidades y los servicios preguntan por claves (`webhooks.enabled`, etc.).
"""

from __future__ import annotations

from typing import Any

from app.models import Empresa, PlanSuscripcion, PlanTipo


# Matriz comercial inicial (Trial / Start / Grow / Scale / Enterprise).
# Claves estables; los nombres comerciales pueden cambiar sin tocar el código.
ENTITLEMENT_MATRIX: dict[str, dict[str, Any]] = {
    PlanTipo.TRIAL.value: {
        "public_api.enabled": True,
        "public_api.requests_per_minute": 60,
        "public_api.credentials_max": 2,
        "public_api.write_enabled": True,
        "webhooks.enabled": True,
        "webhooks.endpoints_max": 2,
        "webhooks.retention_days": 7,
        "webhooks.manual_retry": True,
        "webhooks.auto_disable_after": 10,
    },
    PlanTipo.BASICO.value: {  # Start
        "public_api.enabled": True,
        "public_api.requests_per_minute": 60,
        "public_api.credentials_max": 3,
        "public_api.write_enabled": True,
        "webhooks.enabled": True,
        "webhooks.endpoints_max": 3,
        "webhooks.retention_days": 14,
        "webhooks.manual_retry": True,
        "webhooks.auto_disable_after": 15,
    },
    "grow": {
        "public_api.enabled": True,
        "public_api.requests_per_minute": 90,
        "public_api.credentials_max": 5,
        "public_api.write_enabled": True,
        "webhooks.enabled": True,
        "webhooks.endpoints_max": 5,
        "webhooks.retention_days": 30,
        "webhooks.manual_retry": True,
        "webhooks.auto_disable_after": 15,
    },
    PlanTipo.PROFESIONAL.value: {  # Scale
        "public_api.enabled": True,
        "public_api.requests_per_minute": 120,
        "public_api.credentials_max": 10,
        "public_api.write_enabled": True,
        "webhooks.enabled": True,
        "webhooks.endpoints_max": 10,
        "webhooks.retention_days": 60,
        "webhooks.manual_retry": True,
        "webhooks.auto_disable_after": 20,
    },
    PlanTipo.ENTERPRISE.value: {
        "public_api.enabled": True,
        "public_api.requests_per_minute": 300,
        "public_api.credentials_max": 50,
        "public_api.write_enabled": True,
        "webhooks.enabled": True,
        "webhooks.endpoints_max": 50,
        "webhooks.retention_days": 90,
        "webhooks.manual_retry": True,
        "webhooks.auto_disable_after": 20,
    },
}

_FALLBACK = ENTITLEMENT_MATRIX[PlanTipo.BASICO.value]


def plan_key_for_empresa(empresa_id: int | None) -> str:
    if not empresa_id:
        return PlanTipo.BASICO.value
    sub = (
        PlanSuscripcion.query.filter_by(empresa_id=int(empresa_id), activo=True)
        .order_by(PlanSuscripcion.id.desc())
        .first()
    )
    if sub and sub.plan:
        return str(sub.plan).strip().lower()
    empresa = Empresa.query.get(int(empresa_id)) if empresa_id else None
    if empresa and getattr(empresa, "plan", None):
        return str(empresa.plan).strip().lower()
    return PlanTipo.BASICO.value


def entitlements_for_plan(plan_key: str) -> dict[str, Any]:
    key = (plan_key or "").strip().lower()
    base = dict(_FALLBACK)
    base.update(ENTITLEMENT_MATRIX.get(key, {}))
    return base


def entitlements_for_empresa(empresa_id: int | None) -> dict[str, Any]:
    return entitlements_for_plan(plan_key_for_empresa(empresa_id))


def entitlement(empresa_id: int | None, key: str, default=None):
    return entitlements_for_empresa(empresa_id).get(key, default)


def entitlement_bool(empresa_id: int | None, key: str, default: bool = False) -> bool:
    return bool(entitlement(empresa_id, key, default))


def entitlement_int(empresa_id: int | None, key: str, default: int = 0) -> int:
    try:
        return int(entitlement(empresa_id, key, default) or default)
    except (TypeError, ValueError):
        return default
