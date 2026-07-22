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


def storage_bytes_empresa(empresa_id: int) -> int:
    from app.file_storage import size_for_prefix

    object_total = size_for_prefix(f"empresas/{int(empresa_id)}")
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
        return f"{bytes_val / (1024 * 1024):.1f} MB"
    return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"


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
