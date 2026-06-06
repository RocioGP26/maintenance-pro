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

USER_ROLE_HELP = {
    UserRole.SUPERADMIN.value: "Crear, editar y eliminar en todo el sistema.",
    UserRole.ADMIN.value: "Editar y eliminar registros operativos.",
    UserRole.TECNICO.value: "Editar registros (sin crear ni eliminar).",
    UserRole.USUARIO.value: "Solo consulta (lectura).",
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


def can_assign_role(user, target_role: str) -> bool:
    target = normalize_rol(target_role)
    if target == UserRole.SUPERADMIN.value:
        return _rol(user) == UserRole.SUPERADMIN.value
    return can_manage_equipo(user)


def roles_for_select(user) -> list[tuple[str, str]]:
    """Opciones de rol que el usuario actual puede asignar."""
    items = list(USER_ROLE_LABELS.items())
    if _rol(user) != UserRole.SUPERADMIN.value:
        items = [(k, v) for k, v in items if k != UserRole.SUPERADMIN.value]
    return items


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

DELETE_ENDPOINTS = frozenset(
    {
        "main.activos_delete",
        "main.activos_tipo_delete",
        "main.configuracion_campos_delete",
        "main.proveedores_delete",
    }
)
