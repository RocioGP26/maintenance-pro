"""Roles y permisos de usuario en la plataforma."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from flask_login import AnonymousUserMixin


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    TECNICO = "tecnico"
    USUARIO = "usuario"


# Rol legado → permisos de administrador
_LEGACY_ROLE_MAP = {
    "supervisor": UserRole.ADMIN.value,
    "admin": UserRole.ADMIN.value,
}

USER_ROLE_LABELS = {
    UserRole.SUPERADMIN.value: "Superadministrador",
    UserRole.ADMIN.value: "Administrador",
    UserRole.TECNICO.value: "Técnico",
    UserRole.USUARIO.value: "Usuario",
}

# Etiqueta del rol operativo (tecnico) en empresas con inventario comercial
USER_ROLE_LABELS_INVENTARIO = {
    **USER_ROLE_LABELS,
    UserRole.TECNICO.value: "Vendedor",
}

USER_ROLE_HELP = {
    UserRole.SUPERADMIN.value: "Crear, editar y eliminar en todo el sistema.",
    UserRole.ADMIN.value: "Editar y eliminar registros operativos.",
    UserRole.TECNICO.value: "Editar registros (sin crear ni eliminar).",
    UserRole.USUARIO.value: "Solo consulta (lectura).",
}

USER_ROLE_HELP_INVENTARIO = {
    **USER_ROLE_HELP,
    UserRole.TECNICO.value: "Registrar ventas, compras y stock (sin crear catálogos ni eliminar).",
}


def normalize_rol(rol: Optional[str]) -> str:
    r = (rol or "").strip().lower()
    return _LEGACY_ROLE_MAP.get(r, r)


def _rol(user) -> str:
    if user is None or isinstance(user, AnonymousUserMixin):
        return ""
    if not getattr(user, "is_authenticated", False):
        return ""
    return normalize_rol(getattr(user, "rol", ""))


def can_create(user) -> bool:
    return _rol(user) in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)


def can_edit(user) -> bool:
    return _rol(user) in (
        UserRole.SUPERADMIN.value,
        UserRole.ADMIN.value,
        UserRole.TECNICO.value,
    )


def can_delete(user) -> bool:
    return _rol(user) in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)


def can_manage_config(user) -> bool:
    return _rol(user) == UserRole.SUPERADMIN.value


def can_manage_equipo(user) -> bool:
    return _rol(user) in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)


def is_read_only(user) -> bool:
    return _rol(user) == UserRole.USUARIO.value


def _modulos_empresa(empresa) -> list[str]:
    if empresa is None:
        return []
    from app.modules import modulos_activos_de

    return modulos_activos_de(empresa)


def usa_terminologia_inventario(modulos_activos: list[str] | None) -> bool:
    """True si la empresa usa inventario comercial (rol operativo = Vendedor)."""
    from app.modules import MODULO_INVENTARIO

    mods = modulos_activos or []
    return MODULO_INVENTARIO in mods


def role_display_label(
    rol: Optional[str],
    modulos_activos: list[str] | None = None,
    *,
    empresa=None,
) -> str:
    """Etiqueta visible del rol según módulos de la empresa."""
    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO

    key = normalize_rol(rol)
    mods = modulos_activos if modulos_activos is not None else _modulos_empresa(empresa)
    labels = USER_ROLE_LABELS
    if key == UserRole.TECNICO.value and MODULO_INVENTARIO in mods:
        if MODULO_MANTENIMIENTO in mods:
            return "Vendedor / Técnico"
        labels = USER_ROLE_LABELS_INVENTARIO
    return labels.get(key, USER_ROLE_LABELS.get(key, rol or "—"))


def role_help_map(modulos_activos: list[str] | None = None, *, empresa=None) -> dict[str, str]:
    mods = modulos_activos if modulos_activos is not None else _modulos_empresa(empresa)
    if usa_terminologia_inventario(mods):
        return USER_ROLE_HELP_INVENTARIO
    return USER_ROLE_HELP


def can_assign_role(user, target_role: str) -> bool:
    target = normalize_rol(target_role)
    if target == UserRole.SUPERADMIN.value:
        return _rol(user) == UserRole.SUPERADMIN.value
    return can_manage_equipo(user)


def roles_for_select(
    user,
    modulos_activos: list[str] | None = None,
    *,
    empresa=None,
) -> list[tuple[str, str]]:
    """Opciones de rol que el usuario actual puede asignar."""
    mods = modulos_activos if modulos_activos is not None else _modulos_empresa(empresa)
    keys = list(USER_ROLE_LABELS.keys())
    if _rol(user) != UserRole.SUPERADMIN.value:
        keys = [k for k in keys if k != UserRole.SUPERADMIN.value]
    return [(k, role_display_label(k, modulos_activos=mods)) for k in keys]


def permission_flags(user) -> dict:
    """Banderas para plantillas (perm.crear, perm.editar, …)."""
    return {
        "crear": can_create(user),
        "editar": can_edit(user),
        "eliminar": can_delete(user),
        "config": can_manage_config(user),
        "equipo": can_manage_equipo(user),
        "solo_lectura": is_read_only(user),
    }


# POST permitido para rol Usuario (solo lectura global)
USUARIO_POST_ENDPOINTS = frozenset(
    {
        "main.logout",
        "main.incidencia",
    }
)

CREATE_GET_ENDPOINTS = frozenset(
    {
        "main.activos_new",
        "main.activos_tipo_new",
        "main.ordenes_new",
        "main.inventario_new",
        "main.equipo_new",
        "main.configuracion_campos_new",
    }
)

CONFIG_ENDPOINT_PREFIX = "main.configuracion_"
EQUIPO_MUTATION_ENDPOINTS = frozenset(
    {
        "main.equipo_new",
        "main.equipo_edit",
    }
)

EQUIPO_ENDPOINTS = frozenset(
    {
        "main.equipo_list",
        "main.equipo_new",
        "main.equipo_edit",
        "main.mi_perfil",
    }
)

DELETE_ENDPOINTS = frozenset(
    {
        "main.activos_delete",
        "main.activos_tipo_delete",
        "main.configuracion_campos_delete",
        "main.proveedores_delete",
    }
)
