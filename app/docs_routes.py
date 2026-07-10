"""Sirve el índice maestro Maintix Docs en /docs/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

docs_bp = Blueprint("docs_hub", __name__, url_prefix="/docs")

_ROOT = Path(__file__).resolve().parent.parent / "docs"


@docs_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@docs_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@docs_bp.route("/<path:filename>")
def docs_file(filename: str):
    if ".." in filename:
        abort(404)
    target = (_ROOT / filename).resolve()
    if not str(target).startswith(str(_ROOT.resolve())):
        abort(404)
    if not target.is_file():
        abort(404)
    if filename.endswith(".md"):
        return send_from_directory(_ROOT, filename, mimetype="text/markdown; charset=utf-8")
    if filename.endswith((".yaml", ".yml")):
        return send_from_directory(_ROOT, filename, mimetype="text/yaml; charset=utf-8")
    if filename.endswith(".json"):
        return send_from_directory(_ROOT, filename, mimetype="application/json; charset=utf-8")
    abort(404)


@docs_bp.route("")
def index_no_slash():
    return redirect(url_for("docs_hub.index"))
