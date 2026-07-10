"""Sirve MAG (docs/mag/) — Maintix API Guide en /mag/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

mag_bp = Blueprint("mag", __name__, url_prefix="/mag")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "mag"


@mag_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@mag_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@mag_bp.route("/chapters/<path:filename>")
def chapters(filename: str):
    ch_dir = _ROOT / "chapters"
    target = (ch_dir / filename).resolve()
    if not str(target).startswith(str(ch_dir.resolve())):
        abort(404)
    return send_from_directory(ch_dir, filename)


@mag_bp.route("/<path:filename>")
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
    abort(404)


@mag_bp.route("")
def index_no_slash():
    return redirect(url_for("mag.index"))
