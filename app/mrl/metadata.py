"""Metadata común MRL · MRL-11-META."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.mrl.constants import MRL_VERSION, SYSTEM_USER

_VALID_DOC_PATTERN = re.compile(r"^DOC-\d{3}$")
_REGISTERED_DOC_CODES = frozenset(
    f"DOC-{i:03d}" for i in range(1, 11)
)


@dataclass(frozen=True)
class MRLDocumentMeta:
    """Información común de toda exportación Roustix."""

    doc_code: str
    instance_code: str
    module: str
    title: str
    empresa_id: int
    empresa_nombre: str
    generated_at: datetime
    timezone_name: str
    usuario: str = SYSTEM_USER
    empresa_nit: str | None = None
    locale: str = "es-CO"
    mrl_version: str = MRL_VERSION
    template: str | None = None
    document_version: str = "1.0"
    generated_by: str = "Roustix"
    sistema: str = "Roustix"

    def __post_init__(self) -> None:
        doc = (self.doc_code or "").strip().upper()
        if not _VALID_DOC_PATTERN.match(doc):
            raise ValueError(f"Código DOC inválido: {self.doc_code!r}")
        if doc not in _REGISTERED_DOC_CODES:
            raise ValueError(f"DOC no registrado: {doc}")
        if not (self.instance_code or "").strip():
            raise ValueError("instance_code es obligatorio")
        if not (self.empresa_nombre or "").strip():
            raise ValueError("empresa_nombre es obligatorio")
        if self.empresa_id < 1:
            raise ValueError("empresa_id debe ser positivo")
        if self.generated_at.tzinfo is None:
            raise ValueError("generated_at debe ser timezone-aware (UTC)")

        object.__setattr__(self, "doc_code", doc)

    @property
    def tenant(self) -> int:
        """Alias de empresa_id · tenant Roustix."""
        return self.empresa_id

    @property
    def documento(self) -> str:
        """Alias legible de doc_code."""
        return self.doc_code

    @property
    def version(self) -> str:
        """Versión de la instancia del documento."""
        return self.document_version

    @property
    def fecha(self) -> datetime:
        """Timestamp UTC de generación."""
        return self.generated_at

    def as_header_lines(self) -> tuple[str, ...]:
        """Líneas de metadata para bloque header (Excel/PDF)."""
        return (
            self.empresa_nombre,
            f"NIT: {self.empresa_nit}" if self.empresa_nit else "",
            self.title,
            f"{self.doc_code} · {self.instance_code}",
            f"Módulo: {self.module}",
            f"Usuario: {self.usuario}",
        )

    def as_dict(self) -> dict[str, str | int | None]:
        """Representación serializable para logs y propiedades de archivo."""
        return {
            "documento": self.doc_code,
            "instance_code": self.instance_code,
            "version": self.document_version,
            "empresa": self.empresa_nombre,
            "empresa_nit": self.empresa_nit,
            "tenant": self.empresa_id,
            "usuario": self.usuario,
            "generado_por": self.generated_by,
            "sistema": self.sistema,
            "fecha_utc": self.generated_at.isoformat(),
            "timezone": self.timezone_name,
            "locale": self.locale,
            "module": self.module,
            "title": self.title,
            "mrl_version": self.mrl_version,
            "template": self.template,
        }


def build_sample_metadata(*, empresa_id: int = 1) -> MRLDocumentMeta:
    """Metadata mínima válida para smoke tests (sin datos de negocio)."""
    return MRLDocumentMeta(
        doc_code="DOC-010",
        instance_code="BATCH-20260710",
        module="MRL",
        title="Smoke Test Export",
        empresa_id=empresa_id,
        empresa_nombre="Empresa Demo S.A.S.",
        empresa_nit="900000000-1",
        generated_at=datetime(2026, 7, 10, 15, 30, tzinfo=timezone.utc),
        timezone_name="America/Bogota",
        usuario=SYSTEM_USER,
    )
