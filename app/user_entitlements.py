"""Commercial user-seat limits for a tenant subscription."""

from __future__ import annotations

from app.models import Empresa, PlanTipo, User
from app.permissions import UserRole, normalize_rol
from app.platform_config_service import PLANES_SEED, catalogo_plan_meta, plan_tras_trial


class UserLimitExceeded(ValueError):
    """Raised when an active billable user would exceed the subscribed seats."""


def es_usuario_facturable(*, rol: str, activo: bool) -> bool:
    """Requesters are free; every other active account consumes one seat."""
    return bool(activo) and normalize_rol(rol) != UserRole.SOLICITANTE.value


def limite_usuarios_empresa(empresa: Empresa) -> int | None:
    sub = empresa.plan_activo
    key = sub.plan if sub else PlanTipo.TRIAL.value
    if key == PlanTipo.TRIAL.value:
        key = plan_tras_trial()
    value = catalogo_plan_meta(key).get("max_usuarios")
    if value is None:
        seeded = next((row for row in PLANES_SEED if row["clave"] == key), None)
        value = seeded.get("max_usuarios") if seeded else None
    return int(value) if value is not None else None


def usuarios_facturables(empresa_id: int, *, excluir_user_id: int | None = None) -> int:
    query = User.query.filter(
        User.empresa_id == empresa_id,
        User.activo.is_(True),
        User.rol != UserRole.SOLICITANTE.value,
    )
    if excluir_user_id is not None:
        query = query.filter(User.id != excluir_user_id)
    return query.count()


def validar_cupo_usuario(
    empresa: Empresa,
    *,
    rol: str,
    activo: bool,
    excluir_user_id: int | None = None,
) -> None:
    if not es_usuario_facturable(rol=rol, activo=activo):
        return
    limite = limite_usuarios_empresa(empresa)
    if limite is None:
        return
    usados = usuarios_facturables(empresa.id, excluir_user_id=excluir_user_id)
    if usados >= limite:
        raise UserLimitExceeded(
            f"El plan permite {limite} usuarios facturables activos. "
            "Los usuarios con rol Solicitante no consumen cupo."
        )
