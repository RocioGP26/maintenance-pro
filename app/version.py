"""Metadatos canónicos de versión de la aplicación Roustix.

Este módulo es la única fuente de verdad para la versión SemVer del software.
La revisión Git identifica el build desplegado, pero no modifica la versión.
"""

from __future__ import annotations

import os
import re


__version__ = "1.0.12"

_SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)


def is_valid_semver(value: str) -> bool:
    """Indica si ``value`` cumple SemVer 2.0.0."""
    return bool(_SEMVER_RE.fullmatch(value))


def get_build_commit() -> str | None:
    """Devuelve el SHA corto suministrado por Render o GitHub, si existe."""
    for variable in ("RENDER_GIT_COMMIT", "GITHUB_SHA"):
        value = os.environ.get(variable, "").strip()
        if value:
            return value[:12]
    return None


def get_version_info(*, include_build: bool = True) -> dict[str, str]:
    """Payload público seguro, sin datos de infraestructura ni secretos."""
    payload = {
        "application": "Roustix",
        "version": __version__,
        "release": f"v{__version__}",
    }
    commit = get_build_commit() if include_build else None
    if commit:
        payload["commit"] = commit
    return payload


if not is_valid_semver(__version__):  # pragma: no cover - guardia de importación
    raise RuntimeError(f"Versión de aplicación inválida: {__version__!r}")
