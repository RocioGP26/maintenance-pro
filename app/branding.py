"""Nombre y recursos visuales de la aplicación."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from flask import url_for

if TYPE_CHECKING:
    from app.models import Empresa

APP_NAME = "Mantis"
APP_TAGLINE = "Sistema de gestión"
APP_LOGO_PATH = "img/mantis-logo.png"


def empresa_logo_url_or_none(empresa: Optional["Empresa"]) -> Optional[str]:
    if not empresa or not (empresa.logo or "").strip():
        return None
    logo = empresa.logo.strip()
    if logo.startswith(("http://", "https://")):
        return logo
    return url_for("static", filename=logo)
