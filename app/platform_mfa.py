"""Segundo factor TOTP opcional para el panel de plataforma."""

from __future__ import annotations

import os

import pyotp


def totp_habilitado() -> bool:
    return bool(_totp_secret())


def _totp_secret() -> str:
    return os.environ.get("PLATFORM_ADMIN_TOTP_SECRET", "").strip()


def verificar_totp(code: str) -> bool:
    secret = _totp_secret()
    if not secret:
        return True
    normalized = (code or "").strip().replace(" ", "")
    if not normalized.isdigit() or len(normalized) != 6:
        return False
    return pyotp.TOTP(secret).verify(normalized, valid_window=1)
