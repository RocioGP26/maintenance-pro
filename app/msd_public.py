"""Vista pública MSD — Developer Portal sin ruido interno.

Fuente: docs/msd/chapters/*.md (privada vía /msd/chapters/)
Público: /msd/guide/<slug> HTML limpio para integradores.
"""

from __future__ import annotations

import re
from pathlib import Path

from app.mag_public import markdown_to_html

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "msd" / "chapters"

MSD_GUIDE_CHAPTERS: tuple[dict[str, str], ...] = (
    {
        "slug": "filosofia-ecosistema",
        "file": "01-filosofia-ecosistema.md",
        "num": "01",
        "title": "Filosofía del ecosistema",
        "nav": "Filosofía",
    },
    {
        "slug": "developer-portal",
        "file": "02-developer-portal.md",
        "num": "02",
        "title": "Developer Portal",
        "nav": "Portal",
    },
    {
        "slug": "openapi",
        "file": "03-openapi.md",
        "num": "03",
        "title": "OpenAPI 3.1",
        "nav": "OpenAPI",
    },
    {
        "slug": "sdk-oficiales",
        "file": "04-sdk-oficiales.md",
        "num": "04",
        "title": "SDK oficiales",
        "nav": "SDK",
    },
    {
        "slug": "cli",
        "file": "05-cli.md",
        "num": "05",
        "title": "Roustix CLI",
        "nav": "CLI",
    },
    {
        "slug": "sandbox-explorer",
        "file": "06-sandbox-explorer.md",
        "num": "06",
        "title": "Sandbox y API Explorer",
        "nav": "Sandbox",
    },
    {
        "slug": "quick-start",
        "file": "07-quick-start.md",
        "num": "07",
        "title": "Quick Start",
        "nav": "Quick Start",
    },
    {
        "slug": "colecciones",
        "file": "08-colecciones.md",
        "num": "08",
        "title": "Postman e Insomnia",
        "nav": "Colecciones",
    },
    {
        "slug": "publicacion",
        "file": "09-publicacion.md",
        "num": "09",
        "title": "Publicación",
        "nav": "Publicación",
    },
)

_SLUG_BY_FILE = {c["file"]: c["slug"] for c in MSD_GUIDE_CHAPTERS}
_CHAPTER_BY_SLUG = {c["slug"]: c for c in MSD_GUIDE_CHAPTERS}

_DROP_SECTION_TITLES = re.compile(
    r"(?im)^##+\s+("
    r"Exit Criteria|Estado|Relación con otros documentos|"
    r"Entregables Sprint\s*\d*|Estado Sprint\s*\d*|Sprint\s*\d+\s*·\s*Estado"
    r")\s*$"
)


def slug_for_chapter_file(filename: str) -> str | None:
    name = Path(filename.replace("\\", "/")).name
    return _SLUG_BY_FILE.get(name)


def get_chapter(slug: str) -> dict[str, str] | None:
    return _CHAPTER_BY_SLUG.get(slug)


def neighboring(slug: str) -> tuple[dict[str, str] | None, dict[str, str] | None]:
    ids = [c["slug"] for c in MSD_GUIDE_CHAPTERS]
    try:
        i = ids.index(slug)
    except ValueError:
        return None, None
    prev_c = MSD_GUIDE_CHAPTERS[i - 1] if i > 0 else None
    next_c = MSD_GUIDE_CHAPTERS[i + 1] if i + 1 < len(MSD_GUIDE_CHAPTERS) else None
    return prev_c, next_c


def _rewrite_internal_links(text: str) -> str:
    def repl_md_link(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith("/mpa/") or "mpa/" in target:
            return label
        if "NOMENCLATURE" in target or target.endswith("strategy.md"):
            return label
        if target.endswith(".md") and not target.startswith("http"):
            name = Path(target.split("#")[0]).name
            slug = _SLUG_BY_FILE.get(name)
            if slug:
                frag = ""
                if "#" in target:
                    frag = "#" + target.split("#", 1)[1]
                return f"[{label}](/msd/guide/{slug}{frag})"
            # MAG chapters → guía pública MAG
            if re.match(r"^\d{2}-.+\.md$", name) or "mag" in target.lower():
                mag_slug = name
                mag_slug = re.sub(r"^\d+-", "", mag_slug)
                mag_slug = mag_slug.replace(".md", "")
                # enlaces relativos a mag no están en este catálogo; dejar label
                if "/mag/" in target or target.startswith("../mag"):
                    return label
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_md_link, text)


def sanitize_msd_markdown(raw: str) -> str:
    """Quita Sprints / meta interna; conserva Quick Start, SDK, OpenAPI, Sandbox."""
    text = raw.replace("\r\n", "\n")
    text = re.sub(r"(?m)^\*\*Código:\*\*.*\n+", "", text)
    text = re.sub(r"(?m)^\*\*Suite docs:\*\*.*\n+", "", text)

    lines = text.split("\n")
    out: list[str] = []
    skipping = False
    for line in lines:
        if _DROP_SECTION_TITLES.match(line.strip()):
            skipping = True
            continue
        if skipping:
            if re.match(r"^##\s+", line) and not _DROP_SECTION_TITLES.match(line.strip()):
                skipping = False
            else:
                continue

        if re.search(r"(?i)app/[a-z0-9_./]+", line):
            continue
        if "/mpa/" in line or re.search(r"\bMPA-\d", line):
            if line.strip().startswith("|") or "](/mpa/" in line:
                continue
            line = re.sub(r"\[([^\]]+)\]\(/mpa/[^)]+\)", r"\1", line)

        if re.search(r"(?i)Sprint\s*\d|Exit Criteria|NOMENCLATURE", line):
            if line.strip().startswith("|"):
                line = re.sub(r"(?i)\s*[·•-]?\s*Sprint\s*\d[\w.]*", "", line)
                line = re.sub(r"(?i)\s*Exit Criteria\s*", "", line)
            else:
                line = re.sub(r"(?i)\s*[·•-]?\s*Sprint\s*\d[\w.]*", "", line)
                if re.search(r"(?i)Sprint\s*\d|Exit Criteria|NOMENCLATURE", line):
                    continue

        line = re.sub(r"(?i)\s*·\s*\*\*Entregado\*\*", "", line)
        line = re.sub(r"(?i)\s*·\s*Entregado\b", "", line)
        line = line.replace("✅ Entregado", "Disponible")
        line = line.replace("✅ Completo", "Completo")
        out.append(line)

    text = "\n".join(out)
    text = _rewrite_internal_links(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def load_public_chapter(slug: str) -> tuple[dict[str, str], str] | None:
    meta = get_chapter(slug)
    if not meta:
        return None
    path = _ROOT / meta["file"]
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    cleaned = sanitize_msd_markdown(raw)
    return meta, markdown_to_html(cleaned)
