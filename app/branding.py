"""Nombre y recursos visuales de la aplicación."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from flask import url_for

if TYPE_CHECKING:
    from app.models import Empresa

APP_NAME = "Maintix"
APP_TAGLINE = "Toda la operación. Una sola plataforma."
APP_LOGO_PATH = "img/mantis-logo.png"
PUBLIC_CONTACT_EMAIL = "contacto@maintix.com"


def empresa_logo_url_or_none(empresa: Optional["Empresa"]) -> Optional[str]:
    if not empresa or not (empresa.logo or "").strip():
        return None
    logo = normalizar_logo_empresa(empresa.logo.strip())
    if not logo:
        return None
    if logo.startswith(("http://", "https://")):
        return logo
    return url_for("static", filename=logo)


def normalizar_logo_empresa(logo: str) -> Optional[str]:
    """Permite solo URLs https o rutas relativas bajo uploads/."""
    value = (logo or "").strip()
    if not value:
        return None
    if value.startswith("https://"):
        return value
    if value.startswith("uploads/") and ".." not in value and not value.startswith("//"):
        return value
    return None
