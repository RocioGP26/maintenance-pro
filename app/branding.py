"""Nombre y recursos visuales de la aplicación."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from app.file_storage import key_from_reference, url_for_reference

if TYPE_CHECKING:
    from app.models import Empresa

APP_NAME = "Roustix"
APP_TAGLINE = "Toda la operación. Una sola plataforma."
APP_LOGO_PATH = "img/roustix-logo.svg"
APP_FAVICON_PATH = "img/favicon.svg"
PUBLIC_CONTACT_EMAIL = "contacto@roustix.com"


def empresa_logo_url_or_none(empresa: Optional["Empresa"]) -> Optional[str]:
    if not empresa or not (empresa.logo or "").strip():
        return None
    logo = normalizar_logo_empresa(empresa.logo.strip())
    if not logo:
        return None
    return url_for_reference(logo)


def normalizar_logo_empresa(logo: str) -> Optional[str]:
    """Permite solo URLs https o rutas relativas bajo uploads/."""
    value = (logo or "").strip()
    if not value:
        return None
    if value.startswith("https://"):
        return value
    if key_from_reference(value):
        return value
    if value.startswith("uploads/") and ".." not in value and not value.startswith("//"):
        return value
    return None
