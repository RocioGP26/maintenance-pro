"""Contenido dinámico de la landing pública de Maintix (MKT-05 · MCM)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func

from app import db
from app.branding import APP_TAGLINE, PUBLIC_CONTACT_EMAIL
from app.models import Empresa, Machine, User
from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO
from app.platform_config_service import (
    listar_planes_catalogo,
    plan_a_meta,
    trial_dias,
)

# CTAs oficiales (MKT-05 · unificados en todo el sitio público)
CTA_DEMO = "Solicitar demostración"
CTA_FINAL = "Comenzar prueba gratuita"
CTA_ENTERPRISE = "Solicitar demostración"

PROBLEMA_LANDING: dict[str, Any] = {
    "title": "Tu operación no debería depender de Excel.",
    "situaciones": (
        {"icon": "bi-table", "text": "Hojas duplicadas y versiones distintas del mismo dato"},
        {"icon": "bi-chat-dots", "text": "WhatsApp como sistema operativo"},
        {"icon": "bi-journal-text", "text": "OT en papel sin historial por activo"},
        {"icon": "bi-box-seam", "text": "Diferencias de inventario entre bodega y ventas"},
        {"icon": "bi-diagram-2", "text": "Información dispersa en áreas que no se hablan"},
    ),
    "quote": (
        "Cuando cada área tiene una versión distinta de la información, "
        "las decisiones llegan tarde."
    ),
}

SECTORES_LANDING_MCM: tuple[dict[str, str], ...] = (
    {
        "clave": "industria",
        "etiqueta": "Industria",
        "icon": "bi-building-gear",
        "entrada": "Mantenimiento",
        "dolor": (
            "Equipos detenidos sin aviso, OT en papel o WhatsApp, "
            "historial inexistente por máquina."
        ),
        "mensaje": "La planta deja de depender de la memoria del técnico.",
    },
    {
        "clave": "comercio",
        "etiqueta": "Comercio",
        "icon": "bi-shop",
        "entrada": "Inventario",
        "dolor": (
            "Diferencias de stock entre Excels, ventas sin confirmar existencias "
            "y cartera manual."
        ),
        "mensaje": "Deja de vender a ciegas.",
    },
    {
        "clave": "agro",
        "etiqueta": "Agroindustria",
        "icon": "bi-tree",
        "entrada": "Inventario o Mantenimiento",
        "dolor": (
            "Insumos, bodegas y maquinaria en temporadas — "
            "información repartida en varios archivos."
        ),
        "mensaje": "Un registro para bodega y campo — no tres Excels por temporada.",
    },
    {
        "clave": "talleres",
        "etiqueta": "Talleres",
        "icon": "bi-wrench-adjustable",
        "entrada": "Mantenimiento",
        "dolor": (
            "Vehículos y equipos sin historial unificado, "
            "repuestos y tiempos difíciles de rastrear."
        ),
        "mensaje": "Respondes al cliente con historial completo, no con cuadernos.",
    },
    {
        "clave": "distribucion",
        "etiqueta": "Distribución",
        "icon": "bi-truck",
        "entrada": "Inventario",
        "dolor": (
            "Múltiples bodegas, alto volumen de SKUs y ventas "
            "que prometen stock inexistente."
        ),
        "mensaje": "El vendedor y bodega ven el mismo número — en el momento de la venta.",
    },
)

FEATURES_LANDING: tuple[dict[str, str], ...] = (
    {
        "icon": "bi-diagram-3",
        "title": "Control",
        "text": "Toda la información operativa en un solo lugar — sin Excel disperso.",
    },
    {
        "icon": "bi-clock-history",
        "title": "Trazabilidad",
        "text": "Historial completo de activos, inventario, compras y ventas.",
    },
    {
        "icon": "bi-lightning",
        "title": "Productividad",
        "text": "Menos tiempo buscando datos; más tiempo ejecutando.",
    },
    {
        "icon": "bi-layers",
        "title": "Escalabilidad",
        "text": "Activa nuevos módulos sin migrar de plataforma.",
    },
    {
        "icon": "bi-bar-chart-line",
        "title": "Visibilidad",
        "text": "Dashboards e indicadores para decidir con datos reales.",
    },
    {
        "icon": "bi-shield-check",
        "title": "Datos aislados",
        "text": "Multi-tenant: la información de tu empresa nunca se mezcla.",
    },
)

MODULOS_PRODUCCION: tuple[dict[str, Any], ...] = (
    {
        "clave": MODULO_MANTENIMIENTO,
        "label": "Maintix Maintenance",
        "badge": "En producción",
        "badge_class": "landing-badge--live",
        "descripcion": (
            "Activos, órdenes de trabajo, preventivos, repuestos técnicos "
            "e indicadores de planta."
        ),
        "icon": "bi-wrench-adjustable",
        "bullets": (
            "Activos y órdenes de trabajo",
            "Incidencias y calendario preventivo",
            "Repuestos técnicos e indicadores",
        ),
    },
    {
        "clave": MODULO_INVENTARIO,
        "label": "Maintix Inventory",
        "badge": "En producción",
        "badge_class": "landing-badge--live",
        "descripcion": (
            "Catálogo, compras, ventas, clientes, stock y cartera "
            "en un flujo comercial integrado."
        ),
        "icon": "bi-cart3",
        "bullets": (
            "Productos y alertas de bajo stock",
            "Compras, ventas y cuentas por pagar",
            "Dashboard comercial",
        ),
    },
)

MODULOS_ROADMAP: tuple[dict[str, str], ...] = (
    {"label": "CRM", "icon": "bi-people"},
    {"label": "Purchasing", "icon": "bi-bag-check"},
    {"label": "Analytics", "icon": "bi-graph-up-arrow"},
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
        return f"{plural.capitalize()} ampliados"
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
        is_enterprise = plan.clave == "enterprise"
        short = meta.get("short_label", plan.clave)
        items.append(
            {
                **meta,
                # Los valores del catálogo siguen disponibles para facturación y
                # administración, pero no se exponen en la experiencia pública
                # mientras se valida la estrategia comercial.
                "precio_label": (
                    "Contactar para conocer el precio"
                    if is_enterprise
                    else "Precio disponible próximamente"
                ),
                "features": _plan_features_pricing(meta),
                "cta": CTA_ENTERPRISE if is_enterprise else CTA_FINAL,
                "cta_prompt": (
                    f"Quiero información sobre el plan Enterprise de Maintix"
                    if is_enterprise
                    else f"Quiero probar Maintix con el plan {short}"
                ),
            }
        )
    return items


def sectores_landing() -> list[dict[str, str]]:
    return list(SECTORES_LANDING_MCM)


def public_page_context() -> dict[str, Any]:
    """Contexto compartido nav/footer en páginas públicas."""
    dias = trial_dias()
    return {
        "trial_dias": dias,
        "brand_slogan": APP_TAGLINE,
        "contact_email": PUBLIC_CONTACT_EMAIL,
        "cta_trial": f"Probar gratis {dias} días",
        "cta_demo": CTA_DEMO,
        "cta_final": CTA_FINAL,
    }


def estadisticas_confianza() -> dict[str, Any]:
    empresas = db.session.query(func.count(Empresa.id)).scalar() or 0
    activos = db.session.query(func.count(Machine.id)).scalar() or 0
    dias = trial_dias()

    if empresas >= MIN_EMPRESAS_STATS or activos >= MIN_ACTIVOS_STATS:
        return {
            "modo": "metricas",
            "filas": [
                {"valor": f"{empresas}+", "etiqueta": "Empresas activas"},
                {"valor": f"{activos:,}".replace(",", "."), "etiqueta": "Activos gestionados"},
                {"valor": "SaaS", "etiqueta": "Plataforma modular"},
                {"valor": f"{dias} días", "etiqueta": "Prueba gratuita"},
            ],
        }

    return {
        "modo": "honesto",
        "filas": [
            {"valor": "Multi-tenant", "etiqueta": "Datos aislados por empresa"},
            {"valor": "Modular", "etiqueta": "Maintenance e Inventory"},
            {"valor": f"{dias} días", "etiqueta": "Prueba sin tarjeta"},
            {"valor": "Colombia", "etiqueta": "Operación regional"},
        ],
    }


def landing_context() -> dict[str, Any]:
    ctx = public_page_context()
    ctx.update(
        {
            "estadisticas": estadisticas_confianza(),
            "problema": PROBLEMA_LANDING,
            "features": FEATURES_LANDING,
            "modulos_produccion": MODULOS_PRODUCCION,
            "modulos_roadmap": MODULOS_ROADMAP,
            "sectores": sectores_landing(),
            "planes": planes_landing(),
            "mockups": [
            {
                "modulo": "Maintix Inventory",
                "icon": "bi-cart3",
                "empresa": "El Surtidor SAS",
                "kpis": [
                    {"label": "Ventas hoy", "valor": "$480K", "tone": "success"},
                    {"label": "Bajo stock", "valor": "3", "tone": "warning"},
                    {"label": "Por cobrar", "valor": "2", "tone": "neutral"},
                ],
                "filas": [
                    {
                        "nombre": "Aceite motor 1L",
                        "codigo": "REF-001",
                        "estado": "24 uds.",
                        "tone": "success",
                    },
                    {
                        "nombre": "Filtro de aire universal",
                        "codigo": "REF-002",
                        "estado": "Bajo stock",
                        "tone": "warning",
                    },
                ],
            },
            {
                "modulo": "Maintix Maintenance",
                "icon": "bi-wrench-adjustable",
                "empresa": "Logistic SA",
                "kpis": [
                    {"label": "OT abiertas", "valor": "4", "tone": "neutral"},
                    {"label": "Preventivos", "valor": "12", "tone": "success"},
                    {"label": "Disponibilidad", "valor": "Alta", "tone": "success"},
                ],
                "filas": [
                    {
                        "nombre": "Compresor principal",
                        "codigo": "CPS-001",
                        "estado": "Operativo",
                        "tone": "success",
                    },
                    {
                        "nombre": "Línea de producción A",
                        "codigo": "LP5-001",
                        "estado": "Mantenimiento",
                        "tone": "warning",
                    },
                ],
            },
        ],
        }
    )
    return ctx
