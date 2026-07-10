"""Sirve MSD (docs/msd/) — Maintix SDK & Developer Portal en /msd/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

msd_bp = Blueprint("msd", __name__, url_prefix="/msd")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "msd"


@msd_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


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
    ch_dir = _ROOT / "chapters"
    target = (ch_dir / filename).resolve()
    if not str(target).startswith(str(ch_dir.resolve())):
        abort(404)
    return send_from_directory(ch_dir, filename)


@msd_bp.route("/<path:filename>")
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


@msd_bp.route("")
def index_no_slash():
    return redirect(url_for("msd.index"))
