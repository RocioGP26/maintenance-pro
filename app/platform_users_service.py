"""Usuarios globales — listado y acciones de soporte."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Optional

from sqlalchemy import func, or_

from app import db
from app.models import Empresa, TenantActivityLog, User
from app.permissions import USER_ROLE_LABELS, UserRole, normalize_rol

PLATFORM_ROLE_SHORT = {
    UserRole.SUPERADMIN.value: "Admin",
    UserRole.ADMIN.value: "Admin",
    "supervisor": "Supervisor",
    UserRole.TECNICO.value: "Técnico",
    UserRole.VENDEDOR.value: "Vendedor",
    UserRole.USUARIO.value: "Usuario",
    UserRole.SOLICITANTE.value: "Solicitante",
}

PLATFORM_ROLE_BADGE = {
    UserRole.SUPERADMIN.value: "platform-role platform-role--admin",
    UserRole.ADMIN.value: "platform-role platform-role--admin",
    "supervisor": "platform-role platform-role--supervisor",
    UserRole.TECNICO.value: "platform-role platform-role--tecnico",
    UserRole.VENDEDOR.value: "platform-role platform-role--tecnico",
    UserRole.USUARIO.value: "platform-role platform-role--usuario",
    UserRole.SOLICITANTE.value: "platform-role platform-role--usuario",
}

ESTADO_USUARIO_CHOICES = (
    ("", "Todos los estados"),
    ("activo", "Activos"),
    ("bloqueado", "Bloqueados"),
    ("inactivo", "Inactivos"),
)

ROL_USUARIO_CHOICES = (
    ("", "Todos los roles"),
    (UserRole.SUPERADMIN.value, "Superadmin"),
    (UserRole.ADMIN.value, "Administrador"),
    ("supervisor", "Supervisor"),
    (UserRole.TECNICO.value, "Técnico"),
    (UserRole.VENDEDOR.value, "Vendedor"),
    (UserRole.USUARIO.value, "Usuario"),
    (UserRole.SOLICITANTE.value, "Solicitante"),
)


@dataclass
class UsuarioRow:
    user: User
    empresa_nombre: str
    rol_label: str
    rol_badge: str
    estado: str
    estado_label: str
    estado_badge: str
    avatar_color: str
    iniciales: str


def _estado_usuario(user: User) -> tuple[str, str, str]:
    if user.bloqueado:
        return "bloqueado", "Bloqueado", "platform-user-estado platform-user-estado--bloqueado"
    if not user.activo:
        return "inactivo", "Inactivo", "platform-user-estado platform-user-estado--inactivo"
    return "activo", "Activo", "platform-user-estado platform-user-estado--activo"


def _iniciales_usuario(user: User) -> str:
    nombre = (user.nombre_visible or user.username or "").strip()
    partes = [p for p in nombre.split() if p]
    if len(partes) >= 2:
        return (partes[0][0] + partes[1][0]).upper()
    return (nombre[:2] or "?").upper()


AVATAR_COLORS = (
    "#2563eb", "#7c3aed", "#059669", "#d97706", "#dc2626", "#0891b2", "#4f46e5", "#be185d",
)


def usuario_a_fila(user: User) -> UsuarioRow:
    rol_key = normalize_rol(user.rol)
    estado, estado_label, estado_badge = _estado_usuario(user)
    emp = user.empresa
    return UsuarioRow(
        user=user,
        empresa_nombre=emp.razon_social if emp else "—",
        rol_label=PLATFORM_ROLE_SHORT.get(rol_key, USER_ROLE_LABELS.get(rol_key, rol_key)),
        rol_badge=PLATFORM_ROLE_BADGE.get(rol_key, "platform-role"),
        estado=estado,
        estado_label=estado_label,
        estado_badge=estado_badge,
        avatar_color=AVATAR_COLORS[user.id % len(AVATAR_COLORS)],
        iniciales=_iniciales_usuario(user),
    )


def listar_usuarios_platform(
    *,
    empresa_id: str = "",
    rol: str = "",
    estado: str = "",
    q: str = "",
    limit: int = 300,
) -> list[UsuarioRow]:
    query = (
        User.query.outerjoin(Empresa, User.empresa_id == Empresa.id)
        .filter(User.empresa_id.isnot(None))
        .order_by(Empresa.razon_social, User.nombre_visible, User.username)
    )
    if empresa_id:
        try:
            query = query.filter(User.empresa_id == int(empresa_id))
        except ValueError:
            pass
    if rol:
        if rol == "supervisor":
            query = query.filter(User.rol == UserRole.SUPERVISOR.value)
        else:
            query = query.filter(User.rol == rol)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                User.username.ilike(like),
                User.nombre_visible.ilike(like),
                User.email.ilike(like),
                Empresa.razon_social.ilike(like),
            )
        )
    users = query.limit(limit).all()
    filas = [usuario_a_fila(u) for u in users]
    if estado:
        filas = [f for f in filas if f.estado == estado]
    return filas


def kpis_usuarios_platform() -> dict[str, Any]:
    total = User.query.filter(User.empresa_id.isnot(None)).count()
    bloqueados = User.query.filter(User.empresa_id.isnot(None), User.bloqueado.is_(True)).count()
    admins = User.query.filter(
        User.empresa_id.isnot(None),
        User.rol.in_(
            (UserRole.SUPERADMIN.value, UserRole.ADMIN.value, "supervisor", "admin")
        ),
        User.activo.is_(True),
        User.bloqueado.is_(False),
    ).count()
    empresas_con_usuarios = (
        db.session.query(func.count(func.distinct(User.empresa_id)))
        .filter(User.empresa_id.isnot(None))
        .scalar()
    ) or 0
    desde = datetime.utcnow() - timedelta(days=30)
    activos_30 = (
        db.session.query(func.count(func.distinct(TenantActivityLog.user_id)))
        .filter(
            TenantActivityLog.tipo == "login",
            TenantActivityLog.created_at >= desde,
            TenantActivityLog.user_id.isnot(None),
        )
        .scalar()
    ) or 0
    pct_activos = int(round(activos_30 / total * 100)) if total else 0
    promedio_admin = round(admins / empresas_con_usuarios, 1) if empresas_con_usuarios else 0
    return {
        "total": total,
        "activos_30": activos_30,
        "pct_activos_30": pct_activos,
        "admins": admins,
        "promedio_admin": promedio_admin,
        "bloqueados": bloqueados,
        "empresas": empresas_con_usuarios,
    }


def empresas_para_filtro_usuarios() -> list[tuple[str, str]]:
    rows = (
        db.session.query(Empresa.id, Empresa.razon_social)
        .join(User, User.empresa_id == Empresa.id)
        .distinct()
        .order_by(Empresa.razon_social)
        .all()
    )
    return [("", "Todas las empresas"), *[(str(eid), nombre) for eid, nombre in rows]]


def generar_password_temporal() -> str:
    """Genera contraseña temporal que cumple la política mínima."""
    from app.password_policy import MIN_PASSWORD_LENGTH

    while True:
        pwd = secrets.token_urlsafe(12)
        if len(pwd) >= MIN_PASSWORD_LENGTH and any(c.isalpha() for c in pwd) and any(c.isdigit() for c in pwd):
            return pwd


def bloquear_usuario(user: User) -> None:
    user.bloqueado = True
    user.bloqueado_en = datetime.utcnow()


def desbloquear_usuario(user: User) -> None:
    user.bloqueado = False
    user.bloqueado_en = None
