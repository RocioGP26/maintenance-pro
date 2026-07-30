"""Métricas y ciclo de vida de tenants para el panel de plataforma Roustix."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import func, or_

from app import db
from app.models import (
    PLAN_CATALOG,
    Empresa,
    Machine,
    PlanSuscripcion,
    PlanTipo,
    SuscripcionEstado,
    User,
)
from app.permissions import UserRole

ESTADOS_CICLO = (
    ("trial", "Trial"),
    ("activa", "Activa"),
    ("mora", "Mora"),
    ("suspendida", "Suspendida"),
)

ESTADO_META: dict[str, dict[str, str]] = {
    "trial": {"label": "Trial", "badge_class": "platform-badge platform-badge--trial", "icon": "bi-clock"},
    "activa": {"label": "Activa", "badge_class": "platform-badge platform-badge--activa", "icon": ""},
    "mora": {"label": "Mora", "badge_class": "platform-badge platform-badge--mora", "icon": "bi-exclamation-triangle"},
    "suspendida": {
        "label": "Suspendida",
        "badge_class": "platform-badge platform-badge--suspendida",
        "icon": "bi-slash-circle",
    },
}

PLAN_BADGE_CLASS = {
    PlanTipo.TRIAL.value: "platform-plan platform-plan--trial",
    PlanTipo.BASICO.value: "platform-plan platform-plan--starter",
    PlanTipo.PROFESIONAL.value: "platform-plan platform-plan--pro",
    PlanTipo.ENTERPRISE.value: "platform-plan platform-plan--enterprise",
}

AVATAR_COLORS = (
    "#2563eb",
    "#7c3aed",
    "#059669",
    "#d97706",
    "#dc2626",
    "#0891b2",
    "#4f46e5",
    "#be185d",
)


def plan_meta(plan_key: str | None) -> dict[str, Any]:
    from app.platform_config_service import catalogo_plan_meta

    return catalogo_plan_meta(plan_key)


def estado_ciclo_empresa(empresa: Empresa, hoy: date | None = None) -> str:
    hoy = hoy or date.today()
    if empresa.suspendida:
        return SuscripcionEstado.SUSPENDIDA.value
    sub = empresa.plan_activo
    if not sub or not sub.activo:
        return SuscripcionEstado.SUSPENDIDA.value
    estado = (sub.estado_ciclo or "").strip().lower()
    if estado in {e.value for e in SuscripcionEstado}:
        return estado
    if sub.plan == PlanTipo.TRIAL.value:
        if sub.fecha_fin and sub.fecha_fin < hoy:
            return SuscripcionEstado.MORA.value
        return SuscripcionEstado.TRIAL.value
    if sub.fecha_fin and sub.fecha_fin < hoy:
        return SuscripcionEstado.MORA.value
    return SuscripcionEstado.ACTIVA.value


def _uploads_root() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "static", "uploads", "empresas")


def _include_legacy_uploads() -> bool:
    from flask import current_app

    from app.file_storage import _backend

    configured = current_app.config.get("STORAGE_INCLUDE_LEGACY_UPLOADS")
    if configured is None:
        # En R2/S3 el prefijo empresas/ es la fuente de verdad (cutover S0).
        return _backend() != "s3"
    return bool(configured)


def storage_bytes_empresa(empresa_id: int) -> int:
    from app.file_storage import size_for_prefix

    object_total = size_for_prefix(f"empresas/{int(empresa_id)}")
    if not _include_legacy_uploads():
        return object_total
    carpeta = os.path.join(_uploads_root(), str(empresa_id))
    if not os.path.isdir(carpeta):
        return object_total
    total = object_total
    for raiz, _dirs, archivos in os.walk(carpeta):
        for nombre in archivos:
            try:
                total += os.path.getsize(os.path.join(raiz, nombre))
            except OSError:
                pass
    return total


def _format_storage(bytes_val: int) -> str:
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    if bytes_val < 1024 * 1024 * 1024:
        mb = bytes_val / (1024 * 1024)
        if abs(mb - round(mb)) < 0.05:
            return f"{int(round(mb))} MB"
        return f"{mb:.1f} MB"
    gb = bytes_val / (1024 * 1024 * 1024)
    if abs(gb - round(gb)) < 0.05:
        return f"{int(round(gb))} GB"
    return f"{gb:.2f} GB"


def _format_quota_mb(quota_mb: int) -> str:
    """Etiqueta amigable de cupo (1 GB, 5 GB, 2048 MB, …)."""
    q = int(quota_mb)
    if q >= 1024 and q % 1024 == 0:
        return f"{q // 1024} GB"
    return f"{q} MB"


# Cupos de infraestructura de referencia (piloto · Render Starter + R2 free).
INFRA_DB_QUOTA_MB = 256
INFRA_FILES_QUOTA_GB = 10
STORAGE_WARN_PCT = 80


def _storage_uso_pct(used_bytes: int, quota_mb: Optional[int]) -> Optional[int]:
    if quota_mb is None or quota_mb <= 0:
        return None
    quota_bytes = int(quota_mb) * 1024 * 1024
    if quota_bytes <= 0:
        return None
    # Entero truncado: evita anunciar 80 % o 100 % antes de alcanzar realmente
    # el umbral correspondiente.
    return min(100, max(0, int(used_bytes) * 100 // quota_bytes))


def storage_uso_tenant(empresa: Empresa | None) -> Optional[dict[str, Any]]:
    """Uso de archivos del tenant vs cupo efectivo (plan + add-ons).

    Retorna None si no hay empresa o cuota. `warn` es True al ≥ STORAGE_WARN_PCT (80%).
    """
    if empresa is None or not getattr(empresa, "id", None):
        return None
    from app.storage_quota import (
        ADDON_STG_2G_LABEL,
        ADDON_STG_2G_PRICE_LABEL,
        ADDON_STG_2G_SKU,
        addon_storage_mb,
        has_addon_stg_2g,
        quota_mb_efectiva,
    )

    quota_mb = quota_mb_efectiva(empresa)
    if quota_mb is None or int(quota_mb) <= 0:
        return None
    used = storage_bytes_empresa(int(empresa.id))
    quota_bytes = int(quota_mb) * 1024 * 1024
    pct = _storage_uso_pct(used, int(quota_mb))
    addon_mb = addon_storage_mb(empresa)
    plan = getattr(empresa, "plan_activo", None)
    plan_key = getattr(plan, "plan", None) or PlanTipo.TRIAL.value
    meta = plan_meta(plan_key)
    return {
        "empresa_nombre": (getattr(empresa, "razon_social", None) or "").strip() or "Tu empresa",
        "plan_key": plan_key,
        "plan_label": meta.get("label") or meta.get("short_label") or plan_key,
        "used_bytes": used,
        "used_label": _format_storage(used),
        "quota_mb": int(quota_mb),
        "quota_label": _format_quota_mb(int(quota_mb)),
        "pct": pct,
        "warn": pct is not None and pct >= STORAGE_WARN_PCT,
        "uploads_blocked": used >= quota_bytes,
        "over_quota": used > quota_bytes,
        "addon_mb": addon_mb,
        "addon_active": has_addon_stg_2g(empresa),
        "addon_label": ADDON_STG_2G_LABEL,
        "addon_price_label": ADDON_STG_2G_PRICE_LABEL,
        "addon_sku": ADDON_STG_2G_SKU,
    }


def database_size_bytes() -> Optional[int]:
    """Tamaño aproximado de la BD activa (PostgreSQL o SQLite)."""
    from flask import current_app
    from sqlalchemy import text

    uri = (current_app.config.get("SQLALCHEMY_DATABASE_URI") or "").strip()
    try:
        if uri.startswith("sqlite"):
            path = uri.split("sqlite:///")[-1]
            if path and os.path.isfile(path):
                return os.path.getsize(path)
            return None
        if "postgresql" in uri or "postgres" in uri:
            row = db.session.execute(text("SELECT pg_database_size(current_database())")).scalar()
            return int(row) if row is not None else None
    except Exception:
        return None
    return None


def files_storage_total_bytes() -> int:
    """Consumo agregado de archivos (prefijo empresas/ + uploads legacy opcional)."""
    from app.file_storage import size_for_prefix

    total = 0
    try:
        total += size_for_prefix("empresas")
    except Exception:
        pass
    if not _include_legacy_uploads():
        return total
    root = _uploads_root()
    if os.path.isdir(root):
        for raiz, _dirs, archivos in os.walk(root):
            for nombre in archivos:
                try:
                    total += os.path.getsize(os.path.join(raiz, nombre))
                except OSError:
                    pass
    return total


def infra_snapshot(*, probe_smtp: bool = True) -> dict[str, Any]:
    """Monitor interno SuperAdmin: BD, R2 y servicios operativos."""
    from app.infra_status import service_statuses

    db_bytes = database_size_bytes()
    db_quota = INFRA_DB_QUOTA_MB * 1024 * 1024
    files_bytes = files_storage_total_bytes()
    files_quota = INFRA_FILES_QUOTA_GB * 1024 * 1024 * 1024
    db_pct = (
        min(100, int(round(db_bytes / db_quota * 100)))
        if db_bytes is not None and db_quota
        else None
    )
    files_pct = min(100, int(round(files_bytes / files_quota * 100))) if files_quota else None
    return {
        "database": {
            "label": "PostgreSQL",
            "used_bytes": db_bytes,
            "used_label": _format_storage(db_bytes) if db_bytes is not None else "No disponible",
            "quota_label": f"{INFRA_DB_QUOTA_MB} MB",
            "pct": db_pct,
            "warn": db_pct is not None and db_pct >= STORAGE_WARN_PCT,
        },
        "files": {
            "label": "Cloudflare R2",
            "used_bytes": files_bytes,
            "used_label": _format_storage(files_bytes),
            "quota_label": f"{INFRA_FILES_QUOTA_GB} GB",
            "pct": files_pct,
            "warn": files_pct is not None and files_pct >= STORAGE_WARN_PCT,
        },
        "services": service_statuses(probe_smtp=probe_smtp),
        "notes": (
            f"Límites de referencia del entorno actual: PostgreSQL {INFRA_DB_QUOTA_MB} MB · "
            f"Cloudflare R2 {INFRA_FILES_QUOTA_GB} GB."
        ),
    }


def activos_por_empresa() -> dict[int, int]:
    rows = (
        db.session.query(Machine.empresa_id, func.count(Machine.id))
        .filter(Machine.empresa_id.isnot(None))
        .group_by(Machine.empresa_id)
        .all()
    )
    return {int(eid): int(cnt) for eid, cnt in rows if eid}


def usuarios_por_empresa() -> dict[int, int]:
    rows = (
        db.session.query(User.empresa_id, func.count(User.id))
        .filter(User.empresa_id.isnot(None), User.activo.is_(True))
        .group_by(User.empresa_id)
        .all()
    )
    return {int(eid): int(cnt) for eid, cnt in rows if eid}


def _activos_por_empresa() -> dict[int, int]:
    return activos_por_empresa()


def _usuarios_por_empresa() -> dict[int, int]:
    return usuarios_por_empresa()


def admin_empresa(empresa: Empresa) -> Optional[User]:
    return (
        User.query.filter_by(empresa_id=empresa.id, rol=UserRole.SUPERADMIN.value, activo=True)
        .order_by(User.created_at.asc())
        .first()
    )


@dataclass
class EmpresaRow:
    empresa: Empresa
    estado: str
    plan_key: str
    plan_short: str
    plan_badge_class: str
    activos: int
    max_activos: Optional[int]
    uso_pct: Optional[int]
    storage_bytes: int
    storage_label: str
    storage_quota_mb: Optional[int]
    storage_quota_label: str
    storage_pct: Optional[int]
    storage_warn: bool
    usuarios: int
    admin_nombre: str
    admin_email: str
    avatar_color: str
    mrr: float


def _uso_pct(activos: int, max_activos: Optional[int]) -> Optional[int]:
    if max_activos is None or max_activos <= 0:
        return None
    return min(100, int(round(activos / max_activos * 100)))


def empresa_a_fila(
    empresa: Empresa,
    *,
    activos_map: dict[int, int],
    usuarios_map: dict[int, int],
    hoy: date | None = None,
) -> EmpresaRow:
    hoy = hoy or date.today()
    estado = estado_ciclo_empresa(empresa, hoy)
    plan = empresa.plan_activo
    plan_key = plan.plan if plan else PlanTipo.TRIAL.value
    meta = plan_meta(plan_key)
    activos = activos_map.get(empresa.id, 0)
    storage = storage_bytes_empresa(empresa.id)
    from app.storage_quota import quota_mb_efectiva

    quota_mb = quota_mb_efectiva(empresa)
    storage_pct = _storage_uso_pct(storage, quota_mb)
    adm = admin_empresa(empresa)
    from app.platform_billing import mrr_empresa

    mrr = mrr_empresa(empresa, hoy) if estado in ("activa", "mora") else 0.0
    return EmpresaRow(
        empresa=empresa,
        estado=estado,
        plan_key=plan_key,
        plan_short=meta["short_label"],
        plan_badge_class=meta["badge_class"],
        activos=activos,
        max_activos=meta["max_activos"],
        uso_pct=_uso_pct(activos, meta["max_activos"]),
        storage_bytes=storage,
        storage_label=_format_storage(storage),
        storage_quota_mb=quota_mb,
        storage_quota_label=(
            _format_storage(int(quota_mb) * 1024 * 1024) if quota_mb else "—"
        ),
        storage_pct=storage_pct,
        storage_warn=storage_pct is not None and storage_pct >= STORAGE_WARN_PCT,
        usuarios=usuarios_map.get(empresa.id, 0),
        admin_nombre=(adm.nombre_visible or adm.username) if adm else "—",
        admin_email=(adm.email or "") if adm else "",
        avatar_color=AVATAR_COLORS[empresa.id % len(AVATAR_COLORS)],
        mrr=mrr,
    )


def listar_empresas_platform(
    *,
    sector: str = "",
    plan: str = "",
    estado: str = "",
    q: str = "",
) -> list[EmpresaRow]:
    hoy = date.today()
    query = Empresa.query.order_by(Empresa.razon_social)
    if sector:
        query = query.filter(Empresa.sector == sector)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Empresa.razon_social.ilike(like),
                Empresa.nit.ilike(like),
                Empresa.slug.ilike(like),
            )
        )
    empresas = query.all()
    activos_map = _activos_por_empresa()
    usuarios_map = _usuarios_por_empresa()
    filas = [empresa_a_fila(e, activos_map=activos_map, usuarios_map=usuarios_map, hoy=hoy) for e in empresas]
    if plan:
        filas = [f for f in filas if f.plan_key == plan]
    if estado:
        filas = [f for f in filas if f.estado == estado]
    return filas


def kpis_platform(filas: list[EmpresaRow]) -> dict[str, Any]:
    total = len(filas)
    activas = sum(1 for f in filas if f.estado == "activa")
    trial = sum(1 for f in filas if f.estado == "trial")
    mora = sum(1 for f in filas if f.estado == "mora")
    suspendidas = sum(1 for f in filas if f.estado == "suspendida")
    mrr = sum(f.mrr for f in filas)
    mes_actual = date.today().replace(day=1)
    nuevas_mes = Empresa.query.filter(Empresa.fecha_registro >= datetime.combine(mes_actual, datetime.min.time())).count()
    return {
        "total": total,
        "activas": activas,
        "trial": trial,
        "mora": mora,
        "suspendidas": suspendidas,
        "mrr": mrr,
        "nuevas_mes": nuevas_mes,
        "pct_activas": int(round(activas / total * 100)) if total else 0,
    }


def sector_choices_platform() -> list[tuple[str, str]]:
    from app.platform_config_service import sectores_para_filtro

    return [("", "Todos los sectores"), *sectores_para_filtro()]


def plan_choices_platform() -> list[tuple[str, str]]:
    from app.platform_config_service import listar_planes_catalogo

    items: list[tuple[str, str]] = [
        ("", "Todos los planes"),
        (PlanTipo.TRIAL.value, "Trial"),
    ]
    for plan in listar_planes_catalogo():
        items.append((plan.clave, plan.short_label))
    return items


def estado_choices_platform() -> list[tuple[str, str]]:
    return [("", "Todos los estados"), *ESTADOS_CICLO]
