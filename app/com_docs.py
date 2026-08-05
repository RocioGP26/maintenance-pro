"""Catálogo COM · Commercial Packaging para descarga PDF en SuperAdmin."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_COM_DIR = _ROOT / "docs" / "com"


@dataclass(frozen=True)
class ComPage:
    code: str
    slug: str
    title: str
    description: str
    version: str
    status_label: str
    markdown_name: str
    is_draft: bool = False


PAGES: dict[str, ComPage] = {
    "planes": ComPage(
        code="COM-01",
        slug="planes",
        title="Planes y Licenciamiento",
        description="Matriz oficial Start · Business · Enterprise (precios, cupos y storage).",
        version="1.3.2",
        status_label="Estrategia comercial vigente",
        markdown_name="COM-01-planes-licenciamiento.md",
    ),
    "addons": ComPage(
        code="COM-02",
        slug="addons",
        title="Servicios Adicionales (Add-ons)",
        description="Almacenamiento extra, usuarios y servicios profesionales cotizables.",
        version="1.3.2",
        status_label="Estrategia comercial vigente",
        markdown_name="COM-02-servicios-adicionales.md",
    ),
    "piloto": ComPage(
        code="COM-03",
        slug="piloto",
        title="Programa Piloto y Clientes Fundadores",
        description="Cupo de piloto, beneficios fundador y reglas de precio protegido.",
        version="1.3.3",
        status_label="Piloto vigente",
        markdown_name="COM-03-programa-piloto-fundadores.md",
    ),
    "resumen": ComPage(
        code="COM",
        slug="resumen",
        title="Commercial Packaging · Resumen",
        description="Índice COM y matriz vigente del empaquetado comercial.",
        version="1.3.3",
        status_label="Índice vigente",
        markdown_name="README.md",
    ),
}


def get_com_page(slug: str) -> ComPage | None:
    return PAGES.get(slug)


def list_com_pages() -> list[ComPage]:
    order = ("resumen", "planes", "addons", "piloto")
    return [PAGES[k] for k in order if k in PAGES]


def load_com_markdown(slug: str) -> str:
    page = PAGES.get(slug)
    if page is None:
        raise ValueError(f"Documento COM desconocido: {slug}")
    path = _COM_DIR / page.markdown_name
    if not path.is_file():
        raise FileNotFoundError(page.markdown_name)
    return _strip_com_meta(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def load_com_markdown_cached(slug: str) -> str:
    return load_com_markdown(slug)


def clear_com_cache() -> None:
    load_com_markdown_cached.cache_clear()


def _strip_com_meta(text: str) -> str:
    """Quita H1 duplicado y tabla Campo|Valor inicial si existe."""
    lines = text.splitlines()
    if not lines:
        return text
    i = 0
    if lines[0].startswith("# "):
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and lines[i].startswith("| Campo"):
            while i < len(lines) and (lines[i].startswith("|") or not lines[i].strip()):
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
    # Quitar sección de control de cambios al final si existe
    body = "\n".join(lines[i:])
    for marker in ("\n## 6 · Control de cambios\n", "\n| Versión | Cambio |\n"):
        # Keep version tables in COM-03; only strip trailing changelog-style blocks carefully
        pass
    for marker in ("\n## Control de cambios\n",):
        idx = body.find(marker)
        if idx != -1:
            body = body[:idx]
    return body
