"""Ciclo seguro de códigos de verificación de correo empresarial."""

from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta
from enum import Enum

from flask import current_app
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
from app.branding import APP_NAME
from app.email_service import send_templated_email
from app.models import EmailVerification, User


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    INVALID = "invalid"
    EXPIRED = "expired"
    LOCKED = "locked"
    MISSING = "missing"


class ResendCooldown(RuntimeError):
    def __init__(self, seconds: int):
        self.seconds = max(1, seconds)
        super().__init__(f"Espera {self.seconds} segundos antes de reenviar.")


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_RE.fullmatch(normalize_email(value)))


def _now() -> datetime:
    return datetime.utcnow()


def _latest(user: User, *, for_update: bool = False) -> EmailVerification | None:
    query = EmailVerification.query.filter_by(
        empresa_id=user.empresa_id,
        user_id=user.id,
    ).order_by(EmailVerification.created_at.desc(), EmailVerification.id.desc())
    if for_update:
        query = query.with_for_update()
    return query.first()


def _max_attempts() -> int:
    return max(1, int(current_app.config["EMAIL_VERIFICATION_MAX_ATTEMPTS"]))


def issue_verification(user: User, *, enforce_cooldown: bool = False) -> EmailVerification:
    """Invalida desafíos previos, persiste solo el hash y envía un nuevo código."""
    email = normalize_email(user.email)
    if not is_valid_email(email):
        raise ValueError("El usuario administrador necesita un correo válido.")

    now = _now()
    latest = _latest(user, for_update=enforce_cooldown)
    cooldown = max(0, int(current_app.config["EMAIL_VERIFICATION_RESEND_SECONDS"]))
    if enforce_cooldown and latest and latest.sent_at:
        remaining = cooldown - int((now - latest.sent_at).total_seconds())
        if remaining > 0:
            raise ResendCooldown(remaining)

    EmailVerification.query.filter_by(
        empresa_id=user.empresa_id,
        user_id=user.id,
        used_at=None,
    ).update({EmailVerification.used_at: now}, synchronize_session=False)

    code = f"{secrets.randbelow(1_000_000):06d}"
    item = EmailVerification(
        empresa_id=user.empresa_id,
        user_id=user.id,
        email=email,
        code_hash=generate_password_hash(code),
        expires_at=now
        + timedelta(minutes=max(1, int(current_app.config["EMAIL_VERIFICATION_TTL_MINUTES"]))),
        attempts=0,
    )
    db.session.add(item)
    db.session.commit()

    send_templated_email(
        recipient=email,
        subject=f"Tu código de verificación de {APP_NAME}",
        template_name="verification_code",
        context={
            "code": code,
            "user": user,
            "empresa": user.empresa,
            "ttl_minutes": current_app.config["EMAIL_VERIFICATION_TTL_MINUTES"],
        },
    )
    item.sent_at = _now()
    db.session.commit()
    return item


def ensure_verification(user: User) -> EmailVerification | None:
    # El login no debe convertirse en un canal alterno para saltar el cooldown.
    latest = _latest(user)
    if latest is not None:
        return latest
    return issue_verification(user)


def verify_code(user: User, code: str) -> VerificationStatus:
    """Valida un código y consume un intento incluso si el valor es incorrecto."""
    item = _latest(user, for_update=True)
    if item is None or item.used_at is not None:
        return VerificationStatus.MISSING
    if item.expires_at <= _now():
        return VerificationStatus.EXPIRED
    if item.attempts >= _max_attempts():
        return VerificationStatus.LOCKED

    candidate = (code or "").strip()
    if not re.fullmatch(r"\d{6}", candidate) or not check_password_hash(item.code_hash, candidate):
        item.attempts += 1
        db.session.commit()
        if item.attempts >= _max_attempts():
            return VerificationStatus.LOCKED
        return VerificationStatus.INVALID

    now = _now()
    item.used_at = now
    user.empresa.email_verified_at = now
    db.session.commit()
    return VerificationStatus.VERIFIED


def send_welcome_email(user: User) -> None:
    send_templated_email(
        recipient=normalize_email(user.email),
        subject=f"Te damos la bienvenida a {APP_NAME}",
        template_name="welcome",
        context={"user": user, "empresa": user.empresa},
    )


def masked_email(value: str) -> str:
    email = normalize_email(value)
    if "@" not in email:
        return "correo registrado"
    local, domain = email.split("@", 1)
    visible = local[:2] if len(local) > 2 else local[:1]
    return f"{visible}{'*' * max(3, len(local) - len(visible))}@{domain}"
