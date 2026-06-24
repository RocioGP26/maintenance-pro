"""Usuarios: unicidad por empresa y resolución en login."""

from __future__ import annotations

from app.models import Empresa, User


def normalizar_username(username: str | None) -> str:
    return (username or "").strip().lower()


def username_disponible(
    username: str,
    empresa_id: int | None,
    *,
    excluir_user_id: int | None = None,
) -> bool:
    """True si el username está libre dentro del tenant (o entre usuarios de plataforma)."""
    u = normalizar_username(username)
    if len(u) < 3:
        return False
    q = User.query.filter(User.username == u)
    if empresa_id is None:
        q = q.filter(User.empresa_id.is_(None))
    else:
        q = q.filter(User.empresa_id == int(empresa_id))
    if excluir_user_id:
        q = q.filter(User.id != excluir_user_id)
    return q.first() is None


def buscar_usuario_login(
    username: str,
    *,
    empresa_slug: str | None = None,
) -> User | None:
    """
    Localiza usuario por username.
    Con empresa_slug acota al tenant; sin slug, solo si hay un único candidato.
    """
    u = normalizar_username(username)
    if not u:
        return None

    slug = (empresa_slug or "").strip().lower()
    if slug:
        empresa = Empresa.query.filter_by(slug=slug).first()
        if not empresa:
            return None
        return User.query.filter_by(username=u, empresa_id=empresa.id).first()

    candidatos = User.query.filter_by(username=u).all()
    if len(candidatos) == 1:
        return candidatos[0]
    return None


def mensaje_login_ambiguo(username: str) -> str:
    return (
        f"El usuario «{normalizar_username(username)}» existe en varias empresas. "
        "Indica el código de tu empresa en el campo correspondiente."
    )
