"""Contenido dinámico de la landing pública de Mantis."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func

from app import db
from app.models import Empresa, Machine, User
from app.platform_config_service import (
    listar_planes_catalogo,
    plan_a_meta,
    sectores_para_filtro,
    trial_dias,
)

SECTOR_ICONS: dict[str, str] = {
    "logistica": "bi-truck",
    "manufactura": "bi-building-gear",
    "salud": "bi-heart-pulse",
    "mineria": "bi-minecart-loaded",
    "alimentos": "bi-apple",
    "construccion": "bi-bricks",
    "educacion": "bi-mortarboard",
    "industrial": "bi-gear-wide-connected",
}

FEATURES_LANDING: tuple[dict[str, str], ...] = (
    {
        "icon": "bi-sliders",
        "title": "Campos personalizados",
        "text": "Adapta los formularios a tu sector: placas para flota, lotes para alimentos, certificaciones para industrial.",
    },
    {
        "icon": "bi-clipboard-check",
        "title": "Órdenes de trabajo",
        "text": "Preventivo, correctivo y emergencias. Asigna a técnicos internos o proveedores externos sin fricción.",
    },
    {
        "icon": "bi-shop",
        "title": "Gestión de proveedores",
        "text": "Controla contratistas de servicio e insumos, con historial completo de costos y desempeño.",
    },
    {
        "icon": "bi-bar-chart-line",
        "title": "Reportes en tiempo real",
        "text": "MTBF, MTTR, cumplimiento preventivo y disponibilidad de planta calculados automáticamente.",
    },
    {
        "icon": "bi-shield-check",
        "title": "Datos aislados por empresa",
        "text": "Tu información nunca se mezcla con la de otras empresas. Seguridad de nivel empresarial desde el día uno.",
    },
    {
        "icon": "bi-box-seam",
        "title": "Inventario de repuestos",
        "text": "Controla stock crítico y recibe alertas antes de quedarte sin insumos clave para tu operación.",
    },
)

MIN_EMPRESAS_STATS = 8
MIN_ACTIVOS_STATS = 500


def formato_precio_landing(valor: float | int | None, moneda: str = "COP") -> str:
    try:
        n = float(valor or 0)
    except (TypeError, ValueError):
        return "—"
    if n <= 0:
        return "Gratis"
    if n >= 1_000_000:
        m = n / 1_000_000
        label = f"{m:.2f}".rstrip("0").rstrip(".")
        return f"${label}M"
    if n >= 1_000:
        k = n / 1_000
        label = f"{k:.0f}" if k == int(k) else f"{k:.1f}".rstrip("0").rstrip(".")
        return f"${label}K"
    return f"${int(n):,}".replace(",", ".")


def _limite_texto(valor: int | None, singular: str, plural: str) -> str:
    if valor is None or valor >= 999:
        return f"{plural.capitalize()} ilimitados"
    return f"Hasta {valor} {plural if valor != 1 else singular}"


def _plan_features_pricing(meta: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if meta.get("max_usuarios") is not None:
        lines.append(_limite_texto(meta.get("max_usuarios"), "usuario", "usuarios"))
    if meta.get("max_activos") is not None:
        lines.append(_limite_texto(meta.get("max_activos"), "activo", "activos"))
    for feat in meta.get("caracteristicas") or []:
        if feat.get("included") and feat.get("text"):
            lines.append(str(feat["text"]))
    if not lines and meta.get("descripcion"):
        lines.append(str(meta["descripcion"]))
    return lines


def planes_landing() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for plan in listar_planes_catalogo(solo_visibles=True):
        meta = plan_a_meta(plan)
        items.append(
            {
                **meta,
                "precio_label": formato_precio_landing(meta.get("precio_mensual")),
                "features": _plan_features_pricing(meta),
                "cta": "Hablar con ventas" if plan.clave == "enterprise" else "Empezar gratis",
                "cta_prompt": (
                    "Quiero información sobre el plan Enterprise de Mantis"
                    if plan.clave == "enterprise"
                    else f"Quiero empezar con el plan {meta.get('short_label', plan.clave)} de Mantis"
                ),
            }
        )
    return items


def sectores_landing() -> list[dict[str, str]]:
    rows = []
    for clave, etiqueta in sectores_para_filtro():
        rows.append(
            {
                "clave": clave,
                "etiqueta": etiqueta,
                "icon": SECTOR_ICONS.get(clave, "bi-building"),
            }
        )
    return rows


def estadisticas_confianza() -> dict[str, Any]:
    empresas = db.session.query(func.count(Empresa.id)).scalar() or 0
    activos = db.session.query(func.count(Machine.id)).scalar() or 0
    usuarios = db.session.query(func.count(User.id)).filter(User.empresa_id.isnot(None)).scalar() or 0
    dias = trial_dias()

    if empresas >= MIN_EMPRESAS_STATS or activos >= MIN_ACTIVOS_STATS:
        return {
            "modo": "metricas",
            "filas": [
                {"valor": f"{empresas}+", "etiqueta": "Empresas activas"},
                {"valor": f"{activos:,}".replace(",", "."), "etiqueta": "Activos gestionados"},
                {"valor": "99.9%", "etiqueta": "Uptime garantizado"},
                {"valor": f"{dias} días", "etiqueta": "Prueba gratuita"},
            ],
        }

    return {
        "modo": "honesto",
        "filas": [
            {"valor": "Multi-tenant", "etiqueta": "Datos aislados por empresa"},
            {"valor": "Multi-sector", "etiqueta": "Cualquier industria"},
            {"valor": f"{dias} días", "etiqueta": "Prueba sin tarjeta"},
            {"valor": "CMMS real", "etiqueta": "Para equipos de mantenimiento"},
        ],
    }


def landing_context() -> dict[str, Any]:
    dias = trial_dias()
    return {
        "trial_dias": dias,
        "estadisticas": estadisticas_confianza(),
        "features": FEATURES_LANDING,
        "sectores": sectores_landing(),
        "planes": planes_landing(),
        "mockup": {
            "empresa": "Logistic SA",
            "kpis": [
                {"label": "Disponibilidad", "valor": "99.9%", "tone": "success"},
                {"label": "OT Abiertas", "valor": "4", "tone": "neutral"},
                {"label": "MTBF", "valor": "119d", "tone": "neutral"},
            ],
            "activos": [
                {"nombre": "Compresor principal", "codigo": "CPS-001", "estado": "Operativo", "tone": "success"},
                {"nombre": "Línea de producción A", "codigo": "LP5-001", "estado": "Mantenimiento", "tone": "warning"},
                {"nombre": "Motor línea 1", "codigo": "MT5-001", "estado": "Operativo", "tone": "success"},
            ],
        },
    }
