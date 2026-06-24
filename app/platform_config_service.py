"""Configuración global de plataforma: planes, reglas y sectores."""

from __future__ import annotations

import json
import re
from typing import Any, Optional

from sqlalchemy import func

from app import db
from app.models import (
    PLAN_CATALOG,
    CatalogoPlan,
    PlanTipo,
    ReglaPlataforma,
    SectorCatalogo,
)
from app.sector_templates import SECTOR_CHOICES, SECTOR_LABELS

REGLAS_DEFAULT: dict[str, str] = {
    "trial_dias": "14",
    "dias_gracia_mora": "5",
    "dias_periodo_pago": "30",
    "plan_tras_trial": PlanTipo.BASICO.value,
    "dias_alerta_mora": "3",
}

PLANES_SEED: list[dict[str, Any]] = [
    {
        "clave": PlanTipo.BASICO.value,
        "label": "Plan Starter",
        "short_label": "Starter",
        "descripcion": "Para equipos pequeños que empiezan con CMMS",
        "precio_mensual": 280_000,
        "precio_anual": 2_800_000,
        "max_usuarios": 5,
        "max_activos": 20,
        "storage_mb": 500,
        "soporte": "Email",
        "visible_registro": True,
        "destacado": False,
        "orden": 10,
        "caracteristicas": [
            {"text": "Órdenes de trabajo", "included": True},
            {"text": "Dashboard básico", "included": True},
            {"text": "Proveedores", "included": False},
            {"text": "Campos personalizados", "included": False},
        ],
    },
    {
        "clave": PlanTipo.PROFESIONAL.value,
        "label": "Plan Pro",
        "short_label": "Pro",
        "descripcion": "El más elegido por empresas en crecimiento",
        "precio_mensual": 580_000,
        "precio_anual": 5_800_000,
        "max_usuarios": 20,
        "max_activos": 100,
        "storage_mb": 2000,
        "soporte": "Chat",
        "visible_registro": True,
        "destacado": True,
        "orden": 20,
        "caracteristicas": [
            {"text": "Órdenes de trabajo", "included": True},
            {"text": "Dashboard básico", "included": True},
            {"text": "Proveedores", "included": True},
            {"text": "Campos personalizados", "included": True},
        ],
    },
    {
        "clave": PlanTipo.ENTERPRISE.value,
        "label": "Plan Enterprise",
        "short_label": "Enterprise",
        "descripcion": "Para operaciones a escala con requisitos avanzados",
        "precio_mensual": 1_450_000,
        "precio_anual": 14_500_000,
        "max_usuarios": 999,
        "max_activos": 999,
        "storage_mb": 10000,
        "soporte": "Dedicado",
        "visible_registro": True,
        "destacado": False,
        "orden": 30,
        "caracteristicas": [
            {"text": "Todo lo de Pro", "included": True},
            {"text": "API / Integraciones", "included": True},
            {"text": "Esquema de BD dedicado", "included": True},
            {"text": "SLA garantizado", "included": True},
        ],
    },
]


def ensure_platform_config() -> None:
    """Semilla inicial desde defaults si las tablas están vacías."""
    if not ReglaPlataforma.query.first():
        for clave, valor in REGLAS_DEFAULT.items():
            db.session.add(ReglaPlataforma(clave=clave, valor=valor))
    if not CatalogoPlan.query.first():
        for data in PLANES_SEED:
            plan = CatalogoPlan(
                clave=data["clave"],
                label=data["label"],
                short_label=data["short_label"],
                descripcion=data.get("descripcion", ""),
                precio_mensual=float(data.get("precio_mensual", 0)),
                precio_anual=data.get("precio_anual"),
                max_usuarios=data.get("max_usuarios"),
                max_activos=data.get("max_activos"),
                storage_mb=data.get("storage_mb"),
                soporte=data.get("soporte", "Email"),
                visible_registro=bool(data.get("visible_registro", True)),
                destacado=bool(data.get("destacado", False)),
                orden=int(data.get("orden", 0)),
            )
            plan.set_caracteristicas(data.get("caracteristicas", []))
            db.session.add(plan)
    if not SectorCatalogo.query.first():
        for i, (clave, etiqueta) in enumerate(SECTOR_CHOICES):
            db.session.add(
                SectorCatalogo(
                    clave=clave,
                    etiqueta=etiqueta,
                    visible_registro=True,
                    activo=True,
                    orden=i * 10,
                )
            )
    db.session.commit()
    sincronizar_sectores_catalogo()


def sincronizar_sectores_catalogo() -> None:
    """Añade sectores nuevos del código al catálogo de plataforma (p. ej. comercio)."""
    for i, (clave, etiqueta) in enumerate(SECTOR_CHOICES):
        if SectorCatalogo.query.filter_by(clave=clave).first():
            continue
        db.session.add(
            SectorCatalogo(
                clave=clave,
                etiqueta=etiqueta,
                visible_registro=True,
                activo=True,
                orden=i * 10,
            )
        )
    db.session.commit()


def get_regla(clave: str, default: str = "") -> str:
    row = ReglaPlataforma.query.get(clave)
    if row and row.valor is not None:
        return str(row.valor).strip()
    return REGLAS_DEFAULT.get(clave, default)


def get_regla_int(clave: str, default: int = 0) -> int:
    raw = get_regla(clave, str(default))
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def trial_dias() -> int:
    return get_regla_int("trial_dias", 14)


def dias_gracia_mora() -> int:
    return get_regla_int("dias_gracia_mora", 5)


def dias_periodo_pago() -> int:
    return get_regla_int("dias_periodo_pago", 30)


def plan_tras_trial() -> str:
    return get_regla("plan_tras_trial", PlanTipo.BASICO.value)


def _trial_meta() -> dict[str, Any]:
    dias = trial_dias()
    base = PLAN_CATALOG.get(PlanTipo.TRIAL.value, {})
    return {
        "key": PlanTipo.TRIAL.value,
        "label": f"Prueba gratuita {dias} días",
        "short_label": "Trial",
        "descripcion": base.get("descripcion", "Ideal para evaluar la plataforma"),
        "max_activos": base.get("max_activos"),
        "max_usuarios": None,
        "storage_mb": None,
        "precio_mensual": 0,
        "precio_anual": None,
        "dias": dias,
        "soporte": "Email",
        "visible_registro": True,
        "destacado": False,
        "caracteristicas": [],
        "badge_class": "platform-plan platform-plan--trial",
    }


def plan_a_meta(plan: CatalogoPlan) -> dict[str, Any]:
    badge_map = {
        PlanTipo.BASICO.value: "platform-plan platform-plan--starter",
        PlanTipo.PROFESIONAL.value: "platform-plan platform-plan--pro",
        PlanTipo.ENTERPRISE.value: "platform-plan platform-plan--enterprise",
    }

    return {
        "key": plan.clave,
        "label": plan.label,
        "short_label": plan.short_label,
        "descripcion": plan.descripcion,
        "max_activos": plan.max_activos,
        "max_usuarios": plan.max_usuarios,
        "storage_mb": plan.storage_mb,
        "precio_mensual": plan.precio_mensual or 0,
        "precio_anual": plan.precio_anual,
        "dias": None,
        "soporte": plan.soporte,
        "visible_registro": plan.visible_registro,
        "destacado": plan.destacado,
        "caracteristicas": plan.caracteristicas(),
        "badge_class": badge_map.get(plan.clave, "platform-plan"),
        "orden": plan.orden,
        "id": plan.id,
    }


def catalogo_plan_meta(plan_key: str | None) -> dict[str, Any]:
    key = (plan_key or PlanTipo.TRIAL.value).strip().lower()
    if key == PlanTipo.TRIAL.value:
        return _trial_meta()
    row = CatalogoPlan.query.filter_by(clave=key).first()
    if row:
        return plan_a_meta(row)
    base = PLAN_CATALOG.get(key, PLAN_CATALOG.get(PlanTipo.TRIAL.value, {}))
    return {
        "key": key,
        "label": base.get("label", key),
        "short_label": base.get("short_label", key.title()),
        "descripcion": base.get("descripcion", ""),
        "max_activos": base.get("max_activos"),
        "max_usuarios": None,
        "storage_mb": None,
        "precio_mensual": base.get("precio_mensual", 0) or 0,
        "precio_anual": None,
        "dias": base.get("dias"),
        "soporte": "Email",
        "visible_registro": True,
        "destacado": False,
        "caracteristicas": [],
        "badge_class": "platform-plan",
    }


def listar_planes_catalogo(*, solo_visibles: bool = False) -> list[CatalogoPlan]:
    q = CatalogoPlan.query.order_by(CatalogoPlan.orden, CatalogoPlan.clave)
    if solo_visibles:
        q = q.filter(CatalogoPlan.visible_registro.is_(True))
    return q.all()


def planes_para_registro() -> list[tuple[str, dict[str, Any]]]:
    items: list[tuple[str, dict[str, Any]]] = [(PlanTipo.TRIAL.value, _trial_meta())]
    for plan in listar_planes_catalogo(solo_visibles=True):
        items.append((plan.clave, plan_a_meta(plan)))
    return items


def planes_claves_validas() -> set[str]:
    keys = {PlanTipo.TRIAL.value, *{p.clave for p in CatalogoPlan.query.all()}}
    keys.update(PLAN_CATALOG.keys())
    return keys


def sectores_para_registro() -> list[tuple[str, str]]:
    rows = (
        SectorCatalogo.query.filter_by(visible_registro=True, activo=True)
        .order_by(SectorCatalogo.orden, SectorCatalogo.etiqueta)
        .all()
    )
    if rows:
        return [(r.clave, r.etiqueta) for r in rows]
    return list(SECTOR_CHOICES)


def sectores_para_filtro() -> list[tuple[str, str]]:
    rows = (
        SectorCatalogo.query.filter_by(activo=True)
        .order_by(SectorCatalogo.orden, SectorCatalogo.etiqueta)
        .all()
    )
    if rows:
        return [(r.clave, r.etiqueta) for r in rows]
    return list(SECTOR_CHOICES)


def etiqueta_sector(clave: str) -> str:
    key = (clave or "").strip().lower()
    row = SectorCatalogo.query.filter_by(clave=key).first()
    if row:
        return row.etiqueta
    return SECTOR_LABELS.get(key, key or "—")


def listar_sectores_catalogo() -> list[SectorCatalogo]:
    return SectorCatalogo.query.order_by(SectorCatalogo.orden, SectorCatalogo.etiqueta).all()


def reglas_para_formulario() -> dict[str, str]:
    out = dict(REGLAS_DEFAULT)
    for row in ReglaPlataforma.query.all():
        out[row.clave] = row.valor
    return out


def _slug_plan(clave: str) -> str:
    s = re.sub(r"[^a-z0-9_]+", "_", (clave or "").strip().lower())
    return s.strip("_")[:32]


def guardar_plan(plan_id: int, data: dict[str, Any]) -> CatalogoPlan:
    plan = CatalogoPlan.query.get_or_404(plan_id)
    plan.label = (data.get("label") or plan.label).strip()
    plan.short_label = (data.get("short_label") or plan.short_label).strip()
    plan.descripcion = (data.get("descripcion") or "").strip()
    plan.precio_mensual = float(data.get("precio_mensual") or 0)
    pa = data.get("precio_anual")
    plan.precio_anual = float(pa) if pa not in (None, "") else None
    plan.max_usuarios = _int_or_none(data.get("max_usuarios"))
    plan.max_activos = _int_or_none(data.get("max_activos"))
    plan.storage_mb = _int_or_none(data.get("storage_mb"))
    plan.soporte = (data.get("soporte") or plan.soporte).strip()
    plan.visible_registro = data.get("visible_registro") in (True, "1", "on", 1)
    plan.destacado = data.get("destacado") in (True, "1", "on", 1)
    if plan.destacado:
        CatalogoPlan.query.filter(CatalogoPlan.id != plan.id).update(
            {CatalogoPlan.destacado: False}, synchronize_session=False
        )
    feats = data.get("caracteristicas")
    if isinstance(feats, list):
        plan.set_caracteristicas(feats)
    return plan


def crear_plan(data: dict[str, Any]) -> CatalogoPlan:
    clave = _slug_plan(data.get("clave") or data.get("short_label") or "")
    if not clave:
        raise ValueError("Clave de plan inválida.")
    if CatalogoPlan.query.filter_by(clave=clave).first():
        raise ValueError("Ya existe un plan con esa clave.")
    max_orden = db.session.query(func.max(CatalogoPlan.orden)).scalar() or 0
    plan = CatalogoPlan(
        clave=clave,
        label=(data.get("label") or clave).strip(),
        short_label=(data.get("short_label") or clave).strip(),
        descripcion=(data.get("descripcion") or "").strip(),
        precio_mensual=float(data.get("precio_mensual") or 0),
        orden=int(max_orden) + 10,
        visible_registro=True,
    )
    db.session.add(plan)
    db.session.flush()
    return guardar_plan(plan.id, data)


def guardar_reglas(data: dict[str, Any]) -> None:
    for clave in REGLAS_DEFAULT:
        if clave not in data:
            continue
        valor = str(data[clave]).strip()
        row = ReglaPlataforma.query.get(clave)
        if row:
            row.valor = valor
        else:
            db.session.add(ReglaPlataforma(clave=clave, valor=valor))


def guardar_sector(sector_id: int, data: dict[str, Any]) -> SectorCatalogo:
    sector = SectorCatalogo.query.get_or_404(sector_id)
    sector.etiqueta = (data.get("etiqueta") or sector.etiqueta).strip()
    sector.visible_registro = data.get("visible_registro") in (True, "1", "on", 1)
    sector.activo = data.get("activo") in (True, "1", "on", 1)
    return sector


def crear_sector(data: dict[str, Any]) -> SectorCatalogo:
    clave = _slug_plan(data.get("clave") or data.get("etiqueta") or "")
    if not clave:
        raise ValueError("Clave de sector inválida.")
    if SectorCatalogo.query.filter_by(clave=clave).first():
        raise ValueError("Ya existe un sector con esa clave.")
    max_orden = db.session.query(func.max(SectorCatalogo.orden)).scalar() or 0
    sector = SectorCatalogo(
        clave=clave,
        etiqueta=(data.get("etiqueta") or clave).strip(),
        visible_registro=True,
        activo=True,
        orden=int(max_orden) + 10,
    )
    db.session.add(sector)
    return sector


def _int_or_none(val: Any) -> Optional[int]:
    if val in (None, ""):
        return None
    try:
        return int(val)
    except (TypeError, ValueError):
        return None


def parse_caracteristicas_form(form) -> list[dict]:
    textos = form.getlist("feat_text")
    incluidos = set(form.getlist("feat_included"))
    items: list[dict] = []
    for i, texto in enumerate(textos):
        t = (texto or "").strip()
        if not t:
            continue
        items.append({"text": t, "included": str(i) in incluidos})
    return items
