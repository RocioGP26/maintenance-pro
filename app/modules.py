"""Registro de módulos activables por empresa (Mantis modular)."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import Empresa

# Claves persistidas en empresas.modulos_activos (JSON array)
MODULO_MANTENIMIENTO = "mantenimiento"
MODULO_INVENTARIO = "inventario"

MODULOS_VALIDOS = frozenset({MODULO_MANTENIMIENTO, MODULO_INVENTARIO})

MODULO_META = {
    MODULO_MANTENIMIENTO: {
        "label": "Mantenimiento",
        "short": "Mantenimiento",
        "descripcion": (
            "Activos, órdenes de trabajo, calendario, repuestos técnicos "
            "y proveedores de servicio."
        ),
        "icon": "bi-wrench-adjustable",
    },
    MODULO_INVENTARIO: {
        "label": "Inventario comercial",
        "short": "Inventario",
        "descripcion": (
            "Catálogo de productos, compras a proveedores comerciales, "
            "ventas y control de stock para tiendas."
        ),
        "icon": "bi-cart3",
    },
}

# Prefijos de endpoint → módulo requerido (None = núcleo, siempre visible)
_ENDPOINT_PREFIX_MODULO: tuple[tuple[str, str], ...] = (
    ("main.activos", MODULO_MANTENIMIENTO),
    ("main.ordenes", MODULO_MANTENIMIENTO),
    ("main.calendario", MODULO_MANTENIMIENTO),
    ("main.inventario", MODULO_MANTENIMIENTO),
    ("main.proveedores", MODULO_MANTENIMIENTO),
    ("main.incidencia", MODULO_MANTENIMIENTO),
    ("main.incidencias", MODULO_MANTENIMIENTO),
    ("main.reportes", MODULO_MANTENIMIENTO),
    ("main.configuracion_campos", MODULO_MANTENIMIENTO),
    ("inv_comercial.", MODULO_INVENTARIO),
)


def normalizar_modulos(raw) -> list[str]:
    """Filtra y deduplica módulos válidos preservando orden."""
    if raw is None:
        return [MODULO_MANTENIMIENTO]
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            raw = [m.strip() for m in raw.split(",") if m.strip()]
    if not isinstance(raw, (list, tuple)):
        return [MODULO_MANTENIMIENTO]
    seen: set[str] = set()
    out: list[str] = []
    for item in raw:
        key = (item or "").strip().lower()
        if key in MODULOS_VALIDOS and key not in seen:
            seen.add(key)
            out.append(key)
    return out or [MODULO_MANTENIMIENTO]


def modulos_activos_de(empresa: "Empresa | None") -> list[str]:
    if empresa is None:
        return [MODULO_MANTENIMIENTO]
    return normalizar_modulos(getattr(empresa, "modulos_activos_json", None))


def empresa_tiene_modulo(empresa: "Empresa | None", modulo: str) -> bool:
    return modulo in modulos_activos_de(empresa)


def empresa_solo_inventario(empresa: "Empresa | None") -> bool:
    mods = modulos_activos_de(empresa)
    return MODULO_INVENTARIO in mods and MODULO_MANTENIMIENTO not in mods


def set_modulos_activos(empresa: "Empresa", modulos: list[str]) -> None:
    normalizados = normalizar_modulos(modulos)
    empresa.modulos_activos_json = json.dumps(normalizados, ensure_ascii=False)


def modulo_requerido_por_endpoint(endpoint: str | None) -> str | None:
    if not endpoint:
        return None
    for prefix, modulo in _ENDPOINT_PREFIX_MODULO:
        if endpoint == prefix or endpoint.startswith(prefix):
            return modulo
    return None


def endpoint_exento_modulo(endpoint: str | None) -> bool:
    """Rutas que no exigen comprobación de módulo."""
    if not endpoint:
        return True
    exentos = {
        "main.dashboard",
        "main.index",
        "main.login",
        "main.logout",
        "main.cuenta_suspendida",
        "main.salir_impersonacion",
        "main.configuracion_empresa",
        "main.equipo_list",
        "main.equipo_new",
        "main.equipo_edit",
        "main.mi_perfil",
    }
    if endpoint in exentos:
        return True
    return endpoint.startswith(("static", "onboarding.", "platform.", "tenancy_api.", "admin."))
