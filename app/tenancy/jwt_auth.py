"""Bloque 2 — generar_token() y verificar_token() con JWT firmado."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


def generar_token(
    *,
    user_id: int,
    empresa_id: int,
    empresa_slug: str,
    rol: str,
    secret: str,
    expires_hours: int = 24,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "empresa_id": empresa_id,
        "empresa_slug": empresa_slug,
        "rol": rol,
        "iat": now,
        "exp": now + timedelta(hours=expires_hours),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def verificar_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])
