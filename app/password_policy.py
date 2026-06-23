"""Política de contraseñas compartida."""

from __future__ import annotations

import re

MIN_PASSWORD_LENGTH = 10

PASSWORD_REQUIREMENTS_TEXT = (
    f"Mínimo {MIN_PASSWORD_LENGTH} caracteres, con al menos una letra y un número."
)


def validar_password(password: str) -> str | None:
    """Devuelve mensaje de error o None si la contraseña cumple la política."""
    if not password:
        return "La contraseña es obligatoria."
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres."
    if not re.search(r"[A-Za-z]", password):
        return "La contraseña debe incluir al menos una letra."
    if not re.search(r"\d", password):
        return "La contraseña debe incluir al menos un número."
    return None
