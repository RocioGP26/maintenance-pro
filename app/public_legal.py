"""Catálogo LEG · páginas legales y conversión markdown → HTML."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_LEGAL_DIR = _ROOT / "docs" / "legal"


@dataclass(frozen=True)
class LegalPage:
    code: str
    slug: str
    title: str
    eyebrow: str
    description: str
    version: str
    status_label: str
    is_draft: bool
    markdown_name: str
    # Solo True cuando el documento esté Vigente y se decida publicarlo en la web.
    is_public: bool = False
    category: str = "legal"


PAGES: dict[str, LegalPage] = {
    "terminos": LegalPage(
        code="RTX-LEGAL-001",
        slug="terminos",
        title="Términos y Condiciones",
        eyebrow="RTX-LEGAL-001",
        description="Reglas generales de uso de la plataforma Roustix.",
        version="0.3.0",
        status_label="Borrador · no vigente",
        is_draft=True,
        is_public=False,
        markdown_name="RTX-LEGAL-001-terminos-condiciones.md",
        category="legal",
    ),
    "contrato-saas": LegalPage(
        code="RTX-LEGAL-002",
        slug="contrato-saas",
        title="Contrato de Servicio SaaS",
        eyebrow="RTX-LEGAL-002",
        description="Contrato comercial entre el Prestador y la empresa cliente.",
        version="0.1.0",
        status_label="Borrador · no firmar sin revisión",
        is_draft=True,
        is_public=False,
        markdown_name="RTX-LEGAL-002-contrato-saas.md",
        category="legal",
    ),
    "privacidad": LegalPage(
        code="RTX-PRIV-001",
        slug="privacidad",
        title="Política de Privacidad",
        eyebrow="RTX-PRIV-001",
        description="Política de tratamiento de datos personales de Roustix.",
        version="0.2.0",
        status_label="Borrador · no vigente",
        is_draft=True,
        is_public=False,
        markdown_name="RTX-PRIV-001-politica-privacidad.md",
        category="privacidad",
    ),
    "subencargados": LegalPage(
        code="RTX-PRIV-ANX-001",
        slug="subencargados",
        title="Lista de Subencargados",
        eyebrow="RTX-PRIV-ANX-001",
        description="Proveedores que tratan datos por cuenta de Roustix.",
        version="0.2.0",
        status_label="Borrador operativo",
        is_draft=True,
        is_public=False,
        markdown_name="anexos/RTX-PRIV-ANX-001-subencargados.md",
        category="privacidad",
    ),
    "matriz-conservacion": LegalPage(
        code="RTX-PRIV-ANX-002",
        slug="matriz-conservacion",
        title="Matriz de Conservación",
        eyebrow="RTX-PRIV-ANX-002",
        description="Plazos de conservación por categoría de dato.",
        version="0.2.0",
        status_label="Borrador de plazos",
        is_draft=True,
        is_public=False,
        markdown_name="anexos/RTX-PRIV-ANX-002-matriz-conservacion.md",
        category="privacidad",
    ),
    "flujos-internacionales": LegalPage(
        code="RTX-PRIV-ANX-003",
        slug="flujos-internacionales",
        title="Flujos Internacionales",
        eyebrow="RTX-PRIV-ANX-003",
        description="Registro de transmisiones / transferencias internacionales.",
        version="0.2.0",
        status_label="Borrador · regiones por validar",
        is_draft=True,
        is_public=False,
        markdown_name="anexos/RTX-PRIV-ANX-003-flujos-internacionales.md",
        category="privacidad",
    ),
    "sla": LegalPage(
        code="RTX-SLA-001",
        slug="sla",
        title="Acuerdo de Nivel de Servicio",
        eyebrow="RTX-SLA-001",
        description="Objetivos de disponibilidad y respuesta (anexo opcional).",
        version="0.1.0",
        status_label="Borrador · no vinculante",
        is_draft=True,
        is_public=False,
        markdown_name="RTX-SLA-001-acuerdo-nivel-servicio.md",
        category="operacion",
    ),
    "soporte": LegalPage(
        code="RTX-SUP-001",
        slug="soporte",
        title="Política de Soporte",
        eyebrow="RTX-SUP-001",
        description="Canales, horarios y alcance del soporte al cliente.",
        version="0.1.0",
        status_label="Borrador",
        is_draft=True,
        is_public=False,
        markdown_name="RTX-SUP-001-politica-soporte.md",
        category="operacion",
    ),
    "control-versiones": LegalPage(
        code="RTX-DOC-000",
        slug="control-versiones",
        title="Control de Versiones Documentales",
        eyebrow="RTX-DOC-000",
        description="Índice maestro y reglas de versionado del paquete LEG.",
        version="1.2.0",
        status_label="Activo · gobierno interno",
        is_draft=False,
        is_public=False,
        markdown_name="RTX-DOC-000-control-versiones.md",
        category="gobierno",
    ),
}


def get_legal_page(slug: str) -> LegalPage | None:
    return PAGES.get(slug)


def list_legal_pages() -> list[LegalPage]:
    """Catálogo ordenado para SuperAdmin."""
    order = (
        "control-versiones",
        "terminos",
        "contrato-saas",
        "privacidad",
        "subencargados",
        "matriz-conservacion",
        "flujos-internacionales",
        "sla",
        "soporte",
    )
    return [PAGES[k] for k in order if k in PAGES]


def load_legal_markdown(slug: str) -> str:
    """Texto markdown (sin metadatos internos) para HTML o PDF."""
    page = PAGES.get(slug)
    if page is None:
        raise ValueError(f"Documento legal desconocido: {slug}")
    path = _LEGAL_DIR / page.markdown_name
    if not path.is_file():
        raise FileNotFoundError(page.markdown_name)
    return _strip_for_public(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=16)
def load_legal_html(slug: str) -> str:
    try:
        text = load_legal_markdown(slug)
    except (ValueError, FileNotFoundError):
        return "<p>Documento no disponible.</p>"
    return _markdown_to_html(text)


def clear_legal_cache() -> None:
    load_legal_html.cache_clear()


clear_legal_cache()


def _strip_for_public(text: str) -> str:
    """Quita metadatos de gobierno interno poco útiles en la salida."""
    for marker in (
        "\n## Control de cambios\n",
        "\n## Relación con otros documentos\n",
        "\n## Antes de publicar\n",
        "\n## Anexo A · Checklist antes de firmar",
    ):
        idx = text.find(marker)
        if idx != -1:
            text = text[:idx]
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        i = 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i < len(lines) and lines[i].startswith("| Campo"):
            while i < len(lines) and (lines[i].startswith("|") or not lines[i].strip()):
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
        text = "\n".join(lines[i:])
    return text


def _markdown_to_html(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_buf: list[str] = []

    def flush_para(buf: list[str]) -> None:
        if not buf:
            return
        raw = " ".join(s.strip() for s in buf)
        out.append(f"<p>{_inline(raw)}</p>")
        buf.clear()

    para: list[str] = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            flush_para(para)
            if in_code:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf.clear()
                in_code = False
            else:
                in_code = True
            i += 1
            continue

        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if not stripped:
            flush_para(para)
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].strip()):
            flush_para(para)
            table_lines = [stripped]
            i += 1
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            out.append(_table_html(table_lines))
            continue

        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            flush_para(para)
            level = len(heading.group(1))
            tag = f"h{min(level, 4)}"
            out.append(f"<{tag}>{_inline(heading.group(2))}</{tag}>")
            i += 1
            continue

        if stripped.startswith("> "):
            flush_para(para)
            quote = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            out.append(f"<blockquote><p>{_inline(' '.join(quote))}</p></blockquote>")
            continue

        if re.match(r"^[-*]\s+", stripped):
            flush_para(para)
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.sub(r"^[-*]\s+", "", lines[i].strip()))
                i += 1
            out.append("<ul>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            flush_para(para)
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.sub(r"^\d+\.\s+", "", lines[i].strip()))
                i += 1
            out.append("<ol>" + "".join(f"<li>{_inline(it)}</li>" for it in items) + "</ol>")
            continue

        if stripped == "---":
            flush_para(para)
            out.append("<hr>")
            i += 1
            continue

        para.append(stripped)
        i += 1

    flush_para(para)
    return "\n".join(out)


def _table_html(rows: list[str]) -> str:
    def cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip("|").split("|")]

    header = cells(rows[0])
    body_rows = [cells(r) for r in rows[1:]]
    thead = "<thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in header) + "</tr></thead>"
    tbody_parts = []
    for r in body_rows:
        while len(r) < len(header):
            r.append("")
        tbody_parts.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r[: len(header)]) + "</tr>")
    return (
        '<div class="landing-legal-table-wrap"><table class="landing-legal-table">'
        f"{thead}<tbody>{''.join(tbody_parts)}</tbody></table></div>"
    )


_PUBLIC_LINK_MAP = {
    "RTX-LEGAL-001-terminos-condiciones.md": "/terminos",
    "RTX-PRIV-001-politica-privacidad.md": "/privacidad",
    "../RTX-PRIV-001-politica-privacidad.md": "/privacidad",
    "RTX-SUP-001-politica-soporte.md": "/contacto",
    "RTX-SLA-001-acuerdo-nivel-servicio.md": "/contacto",
    "RTX-LEGAL-002-contrato-saas.md": "/contacto",
    "RTX-DOC-000-control-versiones.md": "/docs/",
}


def _rewrite_public_href(href: str) -> str:
    if href.startswith(("http://", "https://", "mailto:", "/", "#")):
        return href
    name = href.split("/")[-1]
    if href in _PUBLIC_LINK_MAP:
        return _PUBLIC_LINK_MAP[href]
    if name in _PUBLIC_LINK_MAP:
        return _PUBLIC_LINK_MAP[name]
    if "PRIV-ANX" in href or href.startswith("anexos/"):
        return "/privacidad"
    return "/contacto"


def _inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

    def _link(match: re.Match[str]) -> str:
        label, href = match.group(1), html.unescape(match.group(2))
        return f'<a href="{html.escape(_rewrite_public_href(href))}" rel="noopener">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _link, text)
    return text
