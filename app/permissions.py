"""Roles y permisos de usuario en la plataforma."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from flask_login import AnonymousUserMixin


class UserRole(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    TECNICO = "tecnico"
    VENDEDOR = "vendedor"
    USUARIO = "usuario"
    SOLICITANTE = "solicitante"


# Rol legado → permisos de administrador
_LEGACY_ROLE_MAP = {
    "admin": UserRole.ADMIN.value,
}

USER_ROLE_LABELS = {
    UserRole.SUPERADMIN.value: "Superadministrador",
    UserRole.ADMIN.value: "Administrador",
    UserRole.SUPERVISOR.value: "Supervisor",
    UserRole.TECNICO.value: "Técnico",
    UserRole.VENDEDOR.value: "Vendedor",
    UserRole.USUARIO.value: "Usuario — solo consulta",
    UserRole.SOLICITANTE.value: "Solicitante / Reportante",
}

USER_ROLE_HELP = {
    UserRole.SUPERADMIN.value: "Crear, editar y eliminar en todo el sistema.",
    UserRole.ADMIN.value: "Editar y eliminar registros operativos.",
    UserRole.SUPERVISOR.value: "Coordinar, asignar y cambiar estados operativos.",
    UserRole.TECNICO.value: "Editar registros (sin crear ni eliminar).",
    UserRole.VENDEDOR.value: "Gestionar inventario comercial y reportar incidencias.",
    UserRole.USUARIO.value: "Consulta general de los módulos autorizados, sin modificaciones.",
    UserRole.SOLICITANTE.value: "Reportar incidencias y consultar únicamente sus propios reportes.",
}

USER_ROLE_HELP_MANTENIMIENTO = {
    **USER_ROLE_HELP,
    UserRole.ADMIN.value: "Configura activos y OT; asigna técnicos; crea OT desde incidencias.",
    UserRole.TECNICO.value: "Ejecuta OT, registra jornadas y repuestos; puede resolver incidencias.",
    UserRole.USUARIO.value: "Consulta general de mantenimiento, OT, incidencias e indicadores.",
    UserRole.SOLICITANTE.value: "Reporta incidencias y hace seguimiento solo a las propias.",
}

USER_ROLE_HELP_INVENTARIO = {
    **USER_ROLE_HELP,
    UserRole.VENDEDOR.value: "Registrar ventas, compras y stock; puede reportar incidencias.",
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
    return _rol(user) in (
        UserRole.SUPERADMIN.value,
        UserRole.ADMIN.value,
        UserRole.SUPERVISOR.value,
    )


def can_edit(user) -> bool:
    return _rol(user) in (
        UserRole.SUPERADMIN.value,
        UserRole.ADMIN.value,
        UserRole.SUPERVISOR.value,
        UserRole.TECNICO.value,
        UserRole.VENDEDOR.value,
    )


def can_delete(user) -> bool:
    return _rol(user) in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)


def can_manage_config(user) -> bool:
    return _rol(user) == UserRole.SUPERADMIN.value


def can_manage_equipo(user) -> bool:
    return _rol(user) in (UserRole.SUPERADMIN.value, UserRole.ADMIN.value)


def is_read_only(user) -> bool:
    return _rol(user) == UserRole.USUARIO.value


def is_requester(user) -> bool:
    return _rol(user) == UserRole.SOLICITANTE.value


def is_vendor(user) -> bool:
    return _rol(user) == UserRole.VENDEDOR.value


def _modulos_empresa(empresa) -> list[str]:
    if empresa is None:
        return []
    from app.modules import modulos_activos_de

    return modulos_activos_de(empresa)


def usa_terminologia_inventario(modulos_activos: list[str] | None) -> bool:
    """True cuando la empresa tiene habilitado Inventario comercial."""
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
    return USER_ROLE_LABELS.get(key, rol or "—")


def can_report_incident(user) -> bool:
    """El rol de consulta no crea; los roles operativos y solicitante sí reportan."""
    return getattr(user, "is_authenticated", False) and not is_read_only(user)


def can_manage_incidents(user) -> bool:
    """Supervisor / técnico: revisar y resolver incidencias (no rol Usuario)."""
    return _rol(user) in (
        UserRole.SUPERADMIN.value,
        UserRole.ADMIN.value,
        UserRole.SUPERVISOR.value,
        UserRole.TECNICO.value,
    )


def can_access_maintenance(user) -> bool:
    return _rol(user) != UserRole.VENDEDOR.value


def can_access_inventory(user) -> bool:
    return _rol(user) != UserRole.TECNICO.value


def can_create_work_order(user) -> bool:
    """Supervisor / admin: crear OT (p. ej. desde incidencia)."""
    return can_create(user)


def role_help_map(modulos_activos: list[str] | None = None, *, empresa=None) -> dict[str, str]:
    mods = modulos_activos if modulos_activos is not None else _modulos_empresa(empresa)
    if usa_terminologia_inventario(mods):
        return USER_ROLE_HELP_INVENTARIO
    from app.modules import MODULO_MANTENIMIENTO

    if MODULO_MANTENIMIENTO in mods:
        return USER_ROLE_HELP_MANTENIMIENTO
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
    from app.modules import MODULO_INVENTARIO, MODULO_MANTENIMIENTO
    if MODULO_MANTENIMIENTO not in mods:
        keys = [k for k in keys if k != UserRole.TECNICO.value]
    if MODULO_INVENTARIO not in mods:
        keys = [k for k in keys if k != UserRole.VENDEDOR.value]
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
        "solicitante": is_requester(user),
        "vendedor": is_vendor(user),
        "acceso_mantenimiento": can_access_maintenance(user),
        "acceso_inventario": can_access_inventory(user),
        "perfil": getattr(user, "is_authenticated", False),
        "reportar_incidencia": can_report_incident(user),
        "gestionar_incidencias": can_manage_incidents(user),
        "crear_ot": can_create_work_order(user),
    }


# POST permitido para rol Usuario (solo lectura global)
USUARIO_POST_ENDPOINTS = frozenset(
    {
        "main.logout",
        "main.mi_perfil",
    }
)

SOLICITANTE_ENDPOINTS = frozenset(
    {
        "main.logout",
        "main.incidencia",
        "main.incidencias_list",
        "main.incidencias_detail",
        "main.mi_perfil",
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
