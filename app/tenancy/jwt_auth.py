"""Generación y verificación de JWT revocables para identidad tenant."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt


def generar_token(
    *,
    user_id: int,
    empresa_id: int,
    empresa_slug: str,
    rol: str,
    secret: str,
    auth_version: int = 1,
    expires_minutes: int = 480,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "empresa_id": int(empresa_id),
        "empresa_slug": empresa_slug,
        "rol": rol,
        "auth_version": int(auth_version or 1),
        "jti": str(uuid4()),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=max(5, int(expires_minutes))),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verificar_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        secret,
        algorithms=["HS256"],
        options={"require": ["sub", "empresa_id", "auth_version", "iat", "nbf", "exp", "jti"]},
    )
