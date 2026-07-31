"""Restablecimiento self-service de contraseña por correo corporativo."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta

from flask import current_app, has_request_context, url_for
from sqlalchemy import func

from app import db
from app.branding import APP_NAME
from app.email_service import send_templated_email
from app.email_verification_service import is_valid_email, normalize_email
from app.models import Empresa, PasswordReset, User
from app.password_policy import validar_password
from app.session_management import revoke_user_sessions


GENERIC_REQUEST_MESSAGE = (
    "Si el correo está registrado, recibirás un enlace seguro para restablecer la contraseña."
)


def _now() -> datetime:
    return datetime.utcnow()


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256((raw_token or "").encode("utf-8")).hexdigest()


def _ttl_minutes() -> int:
    return max(5, int(current_app.config.get("PASSWORD_RESET_TTL_MINUTES", 60)))


def _reset_action_url(raw_token: str) -> str:
    """URL absoluta del enlace; funciona con o sin request HTTP activo."""

    def _build() -> str:
        return url_for("main.restablecer_contrasena", token=raw_token, _external=True)

    if has_request_context():
        return _build()
    with current_app.test_request_context("/"):
        return _build()


def find_users_for_reset(email: str, *, empresa_slug: str | None = None) -> list[User]:
    """Usuarios activos con ese correo (opcionalmente acotados al tenant)."""
    normalized = normalize_email(email)
    if not is_valid_email(normalized):
        return []

    query = User.query.filter(
        func.lower(User.email) == normalized,
        User.activo.is_(True),
        User.bloqueado.is_(False),
        User.empresa_id.isnot(None),
    )
    slug = (empresa_slug or "").strip().lower()
    if slug:
        empresa = Empresa.query.filter_by(slug=slug).first()
        if empresa is None:
            return []
        query = query.filter(User.empresa_id == empresa.id)
    return query.all()


def request_password_reset(email: str, *, empresa_slug: str | None = None) -> str:
    """Emite tokens y envía correo. Siempre devuelve el mismo mensaje genérico."""
    normalized = normalize_email(email)
    if not is_valid_email(normalized):
        return "Ingresa un correo corporativo válido."

    users = find_users_for_reset(normalized, empresa_slug=empresa_slug)
    ttl = _ttl_minutes()
    now = _now()

    for user in users:
        PasswordReset.query.filter_by(user_id=user.id, used_at=None).update(
            {PasswordReset.used_at: now},
            synchronize_session=False,
        )
        raw = secrets.token_urlsafe(32)
        item = PasswordReset(
            empresa_id=user.empresa_id,
            user_id=user.id,
            email=normalized,
            token_hash=_hash_token(raw),
            expires_at=now + timedelta(minutes=ttl),
        )
        db.session.add(item)
        db.session.flush()

        action_url = _reset_action_url(raw)
        send_templated_email(
            empresa_id=user.empresa_id,
            recipient=normalized,
            subject=f"Restablece tu contraseña de {APP_NAME}",
            template_name="password_reset",
            context={
                "user": user,
                "empresa": user.empresa,
                "action_url": action_url,
                "ttl_minutes": ttl,
            },
            idempotency_key=f"password-reset:{item.id}",
            source_type="password_reset",
            source_id=item.id,
        )

    db.session.commit()
    return GENERIC_REQUEST_MESSAGE


def get_valid_reset(raw_token: str) -> PasswordReset | None:
    token_hash = _hash_token(raw_token)
    if not token_hash or token_hash == _hash_token(""):
        return None
    item = PasswordReset.query.filter_by(token_hash=token_hash).first()
    if item is None or item.used_at is not None:
        return None
    expires = item.expires_at
    if expires is not None and getattr(expires, "tzinfo", None) is not None:
        expires = expires.replace(tzinfo=None)
    if expires is None or expires <= _now():
        return None
    user = item.user
    if user is None or not user.activo or user.bloqueado:
        return None
    return item


def consume_password_reset(raw_token: str, new_password: str) -> str | None:
    """Aplica la nueva contraseña. Devuelve mensaje de error o None si OK."""
    error = validar_password(new_password)
    if error:
        return error

    item = get_valid_reset(raw_token)
    if item is None:
        return "El enlace no es válido o ya expiró. Solicita uno nuevo."

    user = item.user
    user.set_password(new_password)
    user.auth_version = int(user.auth_version or 1) + 1
    item.used_at = _now()
    PasswordReset.query.filter(
        PasswordReset.user_id == user.id,
        PasswordReset.used_at.is_(None),
        PasswordReset.id != item.id,
    ).update({PasswordReset.used_at: item.used_at}, synchronize_session=False)
    db.session.flush()
    revoke_user_sessions(user.id, reason="password_reset")
    db.session.commit()
    return None
