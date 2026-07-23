"""Sirve MAG (docs/mag/) — Roustix API Guide en /mag/.

Público: índice HTML + /mag/guide/<slug> (contenido limpio).
Fuente .md: solo con sesión; URLs antiguas /mag/chapters/*.md
redirigen a la guía HTML (nunca exponen el Markdown en público).
"""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, render_template, send_from_directory, session, url_for
from flask_login import current_user

from app.mag_public import MAG_GUIDE_CHAPTERS, load_public_chapter, neighboring, slug_for_chapter_file

mag_bp = Blueprint("mag", __name__, url_prefix="/mag")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "mag"


def _has_internal_docs_access() -> bool:
    if getattr(current_user, "is_authenticated", False):
        return True
    return bool(session.get("platform_admin"))


@mag_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@mag_bp.route("/guide/<slug>")
def guide(slug: str):
    """Capítulo maquetado para integradores (sin .md crudo)."""
    loaded = load_public_chapter(slug)
    if not loaded:
        abort(404)
    chapter, body_html = loaded
    prev_c, next_c = neighboring(slug)
    return render_template(
        "mag/chapter.html",
        chapter=chapter,
        body_html=body_html,
        chapters=MAG_GUIDE_CHAPTERS,
        prev=prev_c,
        next=next_c,
    )


@mag_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@mag_bp.route("/chapters/<path:filename>")
def chapters(filename: str):
    """Fuente Markdown: interna con login; sin sesión → guía HTML pública."""
    slug = slug_for_chapter_file(filename)
    if not _has_internal_docs_access():
        if slug:
            return redirect(url_for("mag.guide", slug=slug), code=302)
        return redirect(url_for("mag.index"), code=302)

    ch_dir = _ROOT / "chapters"
    target = (ch_dir / filename).resolve()
    if not str(target).startswith(str(ch_dir.resolve())):
        abort(404)
    if not target.is_file():
        abort(404)
    return send_from_directory(ch_dir, filename)


@mag_bp.route("/<path:filename>")
def docs_file(filename: str):
    if ".." in filename:
        abort(404)
    # Evitar servir chapters por la ruta catch-all
    if filename.replace("\\", "/").startswith("chapters/"):
        return redirect(url_for("mag.chapters", filename=filename.split("/", 1)[1]))
    target = (_ROOT / filename).resolve()
    if not str(target).startswith(str(_ROOT.resolve())):
        abort(404)
    if not target.is_file():
        abort(404)
    if filename.endswith(".md"):
        if not _has_internal_docs_access():
            return redirect(url_for("mag.index"), code=302)
        return send_from_directory(_ROOT, filename, mimetype="text/markdown; charset=utf-8")
    abort(404)


@mag_bp.route("")
def index_no_slash():
    return redirect(url_for("mag.index"))
