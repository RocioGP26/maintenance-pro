"""Segundo factor TOTP opcional para el panel de plataforma."""

from __future__ import annotations

import os

import pyotp
from flask import current_app, has_app_context


def totp_habilitado() -> bool:
    return bool(_totp_secret())


def _totp_secret() -> str:
    if has_app_context():
        return str(current_app.config.get("PLATFORM_ADMIN_TOTP_SECRET") or "").strip()
    return os.environ.get("PLATFORM_ADMIN_TOTP_SECRET", "").strip()


def totp_requerido() -> bool:
    if has_app_context():
        return bool(current_app.config.get("PLATFORM_MFA_REQUIRED", False))
    return os.environ.get("PLATFORM_MFA_REQUIRED", "false").strip().lower() in {
        "1", "true", "yes"
    }


def verificar_totp(code: str) -> bool:
    secret = _totp_secret()
    if not secret:
        return True
    normalized = (code or "").strip().replace(" ", "")
    if not normalized.isdigit() or len(normalized) != 6:
        return False
    return pyotp.TOTP(secret).verify(normalized, valid_window=1)
