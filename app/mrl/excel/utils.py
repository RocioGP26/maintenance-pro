"""Utilidades internas del motor Excel MRL."""

from __future__ import annotations

from datetime import datetime

from app.mrl.constants import GENERATED_BY_LABEL, MRL_VERSION
from app.mrl.metadata import MRLDocumentMeta
from app.mrl.utils.dates import format_datetime_latam


def hex_to_openpyxl(color: str) -> str:
    """Convierte #RRGGBB a RRGGBB para openpyxl."""
    value = (color or "").strip().lstrip("#").upper()
    if len(value) != 6:
        raise ValueError(f"Color hex inválido: {color!r}")
    return value


def filename_for_meta(meta: MRLDocumentMeta, extension: str = "xlsx") -> str:
    """Nombre de archivo MRL-STD: {DOC}-{codigo}-{YYYYMMDD}.xlsx"""
    ext = extension.lstrip(".")
    stamp = meta.generated_at.strftime("%Y%m%d")
    safe_instance = (
        meta.instance_code.replace("/", "-").replace("\\", "-").replace(" ", "_")
    )
    return f"{meta.doc_code}-{safe_instance}-{stamp}.{ext}"


def footer_text(meta: MRLDocumentMeta) -> str:
    fecha = format_datetime_latam(meta.generated_at, meta.timezone_name)
    return (
        f"{GENERATED_BY_LABEL} · {meta.sistema} · "
        f"{fecha} · MRL v{meta.mrl_version}"
    )


def meta_generated_at() -> datetime:
    from datetime import timezone

    return datetime.now(timezone.utc)
