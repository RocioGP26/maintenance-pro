"""Slugs únicos para archivos de base de datos por empresa."""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models import Empresa


def slugify_empresa(nombre: str) -> str:
    s = unicodedata.normalize("NFKD", nombre or "").encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return (s or "empresa")[:48]


def slug_unico_empresa(base: str, excluir_id: Optional[int] = None) -> str:
    from app.models import Empresa

    slug = slugify_empresa(base)
    if not slug:
        slug = "empresa"
    candidato = slug
    n = 2
    while True:
        q = Empresa.query.filter_by(slug=candidato)
        if excluir_id:
            q = q.filter(Empresa.id != excluir_id)
        if not q.first():
            return candidato[:48]
        candidato = f"{slug}-{n}"
        n += 1
