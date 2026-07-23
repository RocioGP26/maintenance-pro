"""Sirve MSD (docs/msd/) — Roustix SDK & Developer Portal en /msd/.

Público: índice HTML + /msd/guide/<slug> (contenido limpio).
Fuente .md / strategy / NOMENCLATURE: solo con sesión;
URLs antiguas /msd/chapters/*.md redirigen a la guía HTML.
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, send_from_directory, session, url_for
from flask_login import current_user

from app.msd_public import MSD_GUIDE_CHAPTERS, load_public_chapter, neighboring, slug_for_chapter_file

msd_bp = Blueprint("msd", __name__, url_prefix="/msd")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "msd"

# Meta interna: no se sirve en público
_PRIVATE_ROOT_FILES = frozenset({
    "NOMENCLATURE.md",
    "strategy.md",
    "README.md",
    "changelog.md",
})


def _has_internal_docs_access() -> bool:
    if getattr(current_user, "is_authenticated", False):
        return True
    return bool(session.get("platform_admin"))


@msd_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@msd_bp.route("/guide/<slug>")
def guide(slug: str):
    """Capítulo maquetado para integradores (sin .md crudo)."""
    loaded = load_public_chapter(slug)
    if not loaded:
        abort(404)
    chapter, body_html = loaded
    prev_c, next_c = neighboring(slug)
    return render_template(
        "msd/chapter.html",
        chapter=chapter,
        body_html=body_html,
        chapters=MSD_GUIDE_CHAPTERS,
        prev=prev_c,
        next=next_c,
    )


@msd_bp.route("/collections")
def collections_portal():
    return redirect("/docs/api/collections/README.md")


@msd_bp.route("/openapi")
def openapi_portal():
    return redirect("/api/v1/openapi.yaml")


@msd_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@msd_bp.route("/chapters/<path:filename>")
def chapters(filename: str):
    """Fuente Markdown: interna con login; sin sesión → guía HTML pública."""
    slug = slug_for_chapter_file(filename)
    if not _has_internal_docs_access():
        if slug:
            return redirect(url_for("msd.guide", slug=slug), code=302)
        return redirect(url_for("msd.index"), code=302)

    ch_dir = _ROOT / "chapters"
    target = (ch_dir / filename).resolve()
    if not str(target).startswith(str(ch_dir.resolve())):
        abort(404)
    if not target.is_file():
        abort(404)
    return send_from_directory(ch_dir, filename)


@msd_bp.route("/<path:filename>")
def docs_file(filename: str):
    if ".." in filename:
        abort(404)
    rel = filename.replace("\\", "/")
    if rel.startswith("chapters/"):
        return redirect(url_for("msd.chapters", filename=rel.split("/", 1)[1]))

    target = (_ROOT / filename).resolve()
    if not str(target).startswith(str(_ROOT.resolve())):
        abort(404)
    if not target.is_file():
        abort(404)
    if not filename.endswith(".md"):
        abort(404)

    name = Path(filename).name
    if name in _PRIVATE_ROOT_FILES and not _has_internal_docs_access():
        return redirect(url_for("msd.index"), code=302)

    return send_from_directory(_ROOT, filename, mimetype="text/markdown; charset=utf-8")


@msd_bp.route("")
def index_no_slash():
    return redirect(url_for("msd.index"))
