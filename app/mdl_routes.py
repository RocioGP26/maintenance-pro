"""Sirve MDL (docs/mdl/) como proyecto documental independiente en /mdl/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

mdl_bp = Blueprint("mdl", __name__, url_prefix="/mdl")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "mdl"


@mdl_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@mdl_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@mdl_bp.route("/components/<path:filename>")
def components(filename: str):
    comp_dir = _ROOT / "components"
    target = (comp_dir / filename).resolve()
    if not str(target).startswith(str(comp_dir.resolve())):
        abort(404)
    return send_from_directory(comp_dir, filename)


@mdl_bp.route("/<path:filename>")
def docs_file(filename: str):
    """Sirve markdown y assets del proyecto MDL."""
    if ".." in filename:
        abort(404)
    target = (_ROOT / filename).resolve()
    if not str(target).startswith(str(_ROOT.resolve())):
        abort(404)
    if not target.is_file():
        abort(404)
    if filename.endswith(".md"):
        return send_from_directory(_ROOT, filename, mimetype="text/markdown; charset=utf-8")
    abort(404)


@mdl_bp.route("")
def index_no_slash():
    return redirect(url_for("mdl.index"))
