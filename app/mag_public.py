"""Vista pública MAG — capítulos maquetados sin ruido interno.

Fuente: docs/mag/chapters/*.md (privada vía /mag/chapters/)
Público: /mag/guide/<slug> HTML limpio para integradores.
"""

from __future__ import annotations

import html
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "mag" / "chapters"

# slug público → archivo fuente
MAG_GUIDE_CHAPTERS: tuple[dict[str, str], ...] = (
    {
        "slug": "filosofia-api",
        "file": "01-filosofia-api.md",
        "num": "01",
        "title": "Filosofía de la API",
        "nav": "Filosofía",
    },
    {
        "slug": "autenticacion-jwt",
        "file": "02-autenticacion-jwt.md",
        "num": "02",
        "title": "Autenticación JWT",
        "nav": "Autenticación",
    },
    {
        "slug": "multi-tenant",
        "file": "03-multi-tenant.md",
        "num": "03",
        "title": "Multi-tenant",
        "nav": "Multi-tenant",
    },
    {
        "slug": "recursos",
        "file": "04-recursos.md",
        "num": "04",
        "title": "Recursos REST",
        "nav": "Recursos",
    },
    {
        "slug": "convenciones",
        "file": "05-convenciones-nombres.md",
        "num": "05",
        "title": "Convenciones de nombres",
        "nav": "Convenciones",
    },
    {
        "slug": "errores",
        "file": "06-manejo-errores.md",
        "num": "06",
        "title": "Manejo de errores",
        "nav": "Errores",
    },
    {
        "slug": "versionado",
        "file": "07-versionado.md",
        "num": "07",
        "title": "Versionado",
        "nav": "Versionado",
    },
    {
        "slug": "webhooks",
        "file": "08-webhooks.md",
        "num": "08",
        "title": "Webhooks",
        "nav": "Webhooks",
    },
    {
        "slug": "ejemplos",
        "file": "09-ejemplos.md",
        "num": "09",
        "title": "Ejemplos y SDK",
        "nav": "Ejemplos",
    },
    {
        "slug": "limites",
        "file": "10-limites-buenas-practicas.md",
        "num": "10",
        "title": "Límites y buenas prácticas",
        "nav": "Límites",
    },
)

_SLUG_BY_FILE = {c["file"]: c["slug"] for c in MAG_GUIDE_CHAPTERS}
_CHAPTER_BY_SLUG = {c["slug"]: c for c in MAG_GUIDE_CHAPTERS}


def slug_for_chapter_file(filename: str) -> str | None:
    """Mapea 02-autenticacion-jwt.md → autenticacion-jwt."""
    name = Path(filename.replace("\\", "/")).name
    return _SLUG_BY_FILE.get(name)

# Secciones internas que no van a la vista pública
_DROP_SECTION_TITLES = re.compile(
    r"(?im)^##+\s+(Exit Criteria|Estado|Relación con otros documentos)\s*$"
)

_INTERNAL_LINE = re.compile(
    r"(?i)("
    r"app/[a-z0-9_./]+|"
    r"/mpa/|"
    r"Sprint\s*\d|"
    r"ALIGN|"
    r"SECRET_KEY|"
    r"jwt\.encode|jwt\.decode|"
    r"@tenant_required|"
    r"Flask-Login|"
    r"permissions-plans\.md|"
    r"convergencia planificada|"
    r"Implementación actual|"
    r"implementación en curso"
    r")"
)


def get_chapter(slug: str) -> dict[str, str] | None:
    return _CHAPTER_BY_SLUG.get(slug)


def neighboring(slug: str) -> tuple[dict[str, str] | None, dict[str, str] | None]:
    ids = [c["slug"] for c in MAG_GUIDE_CHAPTERS]
    try:
        i = ids.index(slug)
    except ValueError:
        return None, None
    prev_c = MAG_GUIDE_CHAPTERS[i - 1] if i > 0 else None
    next_c = MAG_GUIDE_CHAPTERS[i + 1] if i + 1 < len(MAG_GUIDE_CHAPTERS) else None
    return prev_c, next_c


def _rewrite_internal_links(text: str) -> str:
    def repl_md_link(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith("/mpa/") or "mpa/" in target:
            return label
        if target.endswith(".md") and not target.startswith("http"):
            name = Path(target.split("#")[0]).name
            slug = _SLUG_BY_FILE.get(name)
            if slug:
                frag = ""
                if "#" in target:
                    frag = "#" + target.split("#", 1)[1]
                return f"[{label}](/mag/guide/{slug}{frag})"
        return match.group(0)

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl_md_link, text)
    return text


def sanitize_mag_markdown(raw: str) -> str:
    """Quita ruido interno; conserva contrato (JWT, endpoints, HTTP, payloads)."""
    text = raw.replace("\r\n", "\n")
    text = re.sub(r"(?m)^\*\*Código:\*\*.*\n+", "", text)

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

        # Descartar líneas internas enteras
        if re.search(r"(?i)app/[a-z0-9_./]+", line):
            continue
        if re.search(r"(?i)@tenant_required|Flask-Login|jwt\.encode|jwt\.decode", line):
            continue
        if re.search(r"(?i)^\*\*Implementación actual:", line):
            continue
        if re.search(r"(?i)implementación en curso", line):
            continue
        if "/mpa/" in line or re.search(r"\bMPA-\d", line):
            if line.strip().startswith("|") or "](/mpa/" in line:
                continue
            line = re.sub(r"\[([^\]]+)\]\(/mpa/[^)]+\)", r"\1", line)

        # Sprint / ALIGN — sacar de prosa y celdas
        if re.search(r"(?i)Sprint\s*\d|ALIGN", line):
            if line.strip().startswith("|"):
                line = re.sub(r"(?i)\s*[·•-]?\s*Sprint\s*\d[\w.]*", "", line)
                line = re.sub(r"(?i)\s*ALIGN\s*", "", line)
            else:
                line = re.sub(
                    r"(?i)Las API keys se implementan\s+en Sprint\s*\d[\w.]*\s*conforme al\s*",
                    "Las API keys se documentan conforme al ",
                    line,
                )
                line = re.sub(r"(?i)\s*en Sprint\s*\d[\w.]*", "", line)
                line = re.sub(r"(?i)Sprint\s*\d[\w.]*\s*(añadirá|añadira|añade)", r"Una versión posterior \1", line)
                line = re.sub(r"(?i)\s*[·•-]?\s*Sprint\s*\d[\w.]*", "", line)
                if re.search(r"(?i)Sprint\s*\d|ALIGN", line):
                    continue

        if "permissions-plans" in line:
            line = re.sub(
                r"\[([^\]]+)\]\([^)]*permissions-plans[^)]*\)",
                "contrato de permisos de la plataforma",
                line,
            )
            line = re.sub(r"\bel contrato de permisos de la plataforma\b", "contrato de permisos de la plataforma", line)

        if "SECRET_KEY" in line:
            line = line.replace("`SECRET_KEY` de la aplicación", "clave de firma del servidor")
            line = line.replace("SECRET_KEY", "clave de firma del servidor")

        line = line.replace("✅ Operativo", "Disponible")
        line = line.replace("📋 MAG v2.0", "Planificado (v2)")
        line = line.replace("📋 Planificado para **MAG v2.0**.", "Planificado para una versión posterior (v2).")
        line = line.replace("**Estado:** 📋 Planificado para **MAG v2.0**.", "**Estado:** planificado para v2.")
        # Suavizar fila API key Bearer con sprint residual
        if "API key Bearer" in line and "automatizaciones" in line:
            line = "| **API key Bearer** | Servicios, ERP, BI y automatizaciones |"

        out.append(line)

    text = "\n".join(out)
    text = _rewrite_internal_links(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Frases rotas por sanitizado
    text = re.sub(
        r"(?i)Las API keys se implementan\s*\n\s*en conforme al\s*",
        "Las API keys se documentan conforme al ",
        text,
    )
    text = re.sub(
        r"(?i)Actualmente\s*\n?\s*acepta JWT o sesión activa\.\s*\n?\s*añadir[áa]?\s*\n?\s*API keys",
        "Las rutas protegidas aceptan JWT o sesión web. Una versión posterior añadirá API keys",
        text,
    )
    text = re.sub(r"(?i)el contrato de permisos", "contrato de permisos", text)
    return text.strip() + "\n"


def markdown_to_html(md: str) -> str:
    """Conversor Markdown mínimo (sin dependencias) orientado a docs MAG."""
    lines = md.split("\n")
    html_parts: list[str] = []
    i = 0
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    in_ul = False
    in_ol = False
    in_table = False
    table_rows: list[list[str]] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False
        if in_ol:
            html_parts.append("</ol>")
            in_ol = False

    def close_table() -> None:
        nonlocal in_table, table_rows
        if not in_table:
            return
        if table_rows:
            html_parts.append('<table class="mag-doc-table">')
            header = table_rows[0]
            html_parts.append("<thead><tr>" + "".join(f"<th>{c}</th>" for c in header) + "</tr></thead>")
            body = table_rows[1:]
            # saltar separador markdown |---|
            if body and all(re.match(r"^:?-+:?$", c.replace(" ", "")) for c in body[0]):
                body = body[1:]
            html_parts.append("<tbody>")
            for row in body:
                html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
            html_parts.append("</tbody></table>")
        in_table = False
        table_rows = []

    def inline_format(text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
        text = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            r'<a href="\2">\1</a>',
            text,
        )
        return text

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            close_lists()
            close_table()
            if not in_code:
                in_code = True
                code_lang = line[3:].strip()
                code_buf = []
            else:
                lang_class = f" language-{html.escape(code_lang)}" if code_lang else ""
                body = html.escape("\n".join(code_buf))
                html_parts.append(f'<pre class="mag-json{lang_class}"><code>{body}</code></pre>')
                in_code = False
            i += 1
            continue
        if in_code:
            code_buf.append(line)
            i += 1
            continue

        if line.strip() == "---":
            close_lists()
            close_table()
            html_parts.append("<hr>")
            i += 1
            continue

        if "|" in line and line.strip().startswith("|"):
            close_lists()
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append([inline_format(c) for c in cells])
            i += 1
            continue
        else:
            close_table()

        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            close_lists()
            level = len(heading.group(1))
            html_parts.append(f"<h{level}>{inline_format(heading.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"^[-*]\s+", line):
            close_table()
            if in_ol:
                html_parts.append("</ol>")
                in_ol = False
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{inline_format(re.sub(r'^[-*]\s+', '', line))}</li>")
            i += 1
            continue

        if re.match(r"^\d+\.\s+", line):
            close_table()
            if in_ul:
                html_parts.append("</ul>")
                in_ul = False
            if not in_ol:
                html_parts.append("<ol>")
                in_ol = True
            html_parts.append(f"<li>{inline_format(re.sub(r'^\d+\.\s+', '', line))}</li>")
            i += 1
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        close_lists()
        # blockquote
        if line.startswith(">"):
            html_parts.append(f'<blockquote class="mag-quote">{inline_format(line.lstrip("> ").strip())}</blockquote>')
        else:
            html_parts.append(f"<p>{inline_format(line)}</p>")
        i += 1

    close_lists()
    close_table()
    if in_code and code_buf:
        body = html.escape("\n".join(code_buf))
        html_parts.append(f'<pre class="mag-json"><code>{body}</code></pre>')
    return "\n".join(html_parts)


def load_public_chapter(slug: str) -> tuple[dict[str, str], str] | None:
    meta = get_chapter(slug)
    if not meta:
        return None
    path = _ROOT / meta["file"]
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8")
    cleaned = sanitize_mag_markdown(raw)
    return meta, markdown_to_html(cleaned)
