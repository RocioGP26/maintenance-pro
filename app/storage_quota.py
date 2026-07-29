"""Cuota de almacenamiento por tenant (plan + add-ons).

Hard-limit P0: rechazar uploads cuando used + net > cuota efectiva.
"""

from __future__ import annotations

from typing import Any, Optional

from app.models import Empresa, PlanTipo

# COM-02 · ADD-STG-2G
ADDON_STG_2G_SKU = "ADD-STG-2G"
ADDON_STG_2G_MB = 2048  # +2 GB
ADDON_STG_2G_LABEL = "+2 GB"
ADDON_STG_2G_PRICE_LABEL = "$100.000 / mes"


class StorageQuotaExceeded(ValueError):
    """El archivo no cabe en el cupo de almacenamiento del tenant."""

    def __init__(
        self,
        message: str,
        *,
        used_bytes: int = 0,
        quota_mb: int = 0,
        additional_bytes: int = 0,
    ) -> None:
        super().__init__(message)
        self.used_bytes = used_bytes
        self.quota_mb = quota_mb
        self.additional_bytes = additional_bytes


def addon_storage_mb(empresa: Empresa | None) -> int:
    """MB de add-ons activos (ADD-STG-*)."""
    if empresa is None:
        return 0
    extra = getattr(empresa, "storage_addon_mb", None)
    if extra is None:
        return 0
    try:
        return max(0, int(extra))
    except (TypeError, ValueError):
        return 0


def has_addon_stg_2g(empresa: Empresa | None) -> bool:
    return addon_storage_mb(empresa) >= ADDON_STG_2G_MB


def set_addon_stg_2g(empresa: Empresa, *, active: bool) -> int:
    """Activa o desactiva el add-on +2 GB. Retorna el nuevo storage_addon_mb."""
    current = addon_storage_mb(empresa)
    if active:
        if current < ADDON_STG_2G_MB:
            empresa.storage_addon_mb = current + ADDON_STG_2G_MB
        else:
            empresa.storage_addon_mb = current
    else:
        empresa.storage_addon_mb = max(0, current - ADDON_STG_2G_MB)
    return int(empresa.storage_addon_mb or 0)


def quota_mb_efectiva(empresa: Empresa | None) -> Optional[int]:
    """Cupo total en MB (plan + add-ons). None = sin límite conocido."""
    if empresa is None or not getattr(empresa, "id", None):
        return None
    from app.platform_service import plan_meta

    plan = empresa.plan_activo
    plan_key = plan.plan if plan else PlanTipo.TRIAL.value
    meta = plan_meta(plan_key)
    base = meta.get("storage_mb")
    if base is None or int(base) <= 0:
        return None
    return int(base) + addon_storage_mb(empresa)


def assert_storage_capacity(
    empresa_id: int,
    additional_bytes: int,
    *,
    replacing_bytes: int = 0,
) -> None:
    """Rechaza si el uso actual + bytes netos supera la cuota efectiva.

    Si no hay empresa o no hay cupo definido, no bloquea.
    Si falla la medición, registra alerta operativa y no bloquea (fail-open).
    """
    net = max(0, int(additional_bytes) - max(0, int(replacing_bytes)))
    if net <= 0:
        return

    from app import db

    try:
        empresa = db.session.get(Empresa, int(empresa_id))
    except Exception:
        # Tests sin schema / BD no lista: no bloquear uploads.
        return
    quota_mb = quota_mb_efectiva(empresa)
    if quota_mb is None:
        return

    from app.platform_service import storage_bytes_empresa

    try:
        used = int(storage_bytes_empresa(int(empresa_id)))
    except Exception as exc:
        from app.observability import emit_operational_alert

        emit_operational_alert(
            "storage",
            "quota_measure_failed",
            f"No se pudo medir storage del tenant {empresa_id}; upload permitido",
            exc=exc,
            dedupe_key=f"storage:quota_measure:{empresa_id}",
        )
        return

    quota_bytes = int(quota_mb) * 1024 * 1024
    if used + net <= quota_bytes:
        return

    raise StorageQuotaExceeded(
        "Has alcanzado el límite de almacenamiento de tu plan. "
        "¿Deseas ampliar tu capacidad? +2 GB por $100.000 / mes — "
        "escribe a contacto@roustix.com.",
        used_bytes=used,
        quota_mb=quota_mb,
        additional_bytes=net,
    )


def empresa_id_from_storage_key(key: str) -> Optional[int]:
    """Extrae el id de empresa de claves ``empresas/{id}/...``."""
    parts = (key or "").strip().replace("\\", "/").lstrip("/").split("/")
    if len(parts) < 2 or parts[0] != "empresas":
        return None
    try:
        return int(parts[1])
    except (TypeError, ValueError):
        return None


def storage_uso_dict(empresa: Empresa | None) -> Optional[dict[str, Any]]:
    """Alias estable para UI; delega en platform_service con cuota efectiva."""
    from app.platform_service import storage_uso_tenant

    return storage_uso_tenant(empresa)
