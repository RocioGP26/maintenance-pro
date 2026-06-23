"""Almacenamiento efímero de contraseña durante el wizard de onboarding."""

from __future__ import annotations

from flask import current_app, session
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

PWD_SALT = "onboarding-pwd-v1"
PWD_SESSION_KEY = "onboarding_pwd_enc"
PWD_MAX_AGE = 3600


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt=PWD_SALT)


def store_onboarding_password(password: str) -> None:
    session[PWD_SESSION_KEY] = _serializer().dumps(password)


def pop_onboarding_password() -> str | None:
    enc = session.pop(PWD_SESSION_KEY, None)
    if not enc:
        return None
    try:
        return _serializer().loads(enc, max_age=PWD_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None


def clear_onboarding_password() -> None:
    session.pop(PWD_SESSION_KEY, None)
