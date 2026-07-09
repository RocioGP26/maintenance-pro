"""Sirve MUX (docs/mux/) — Maintix User Experience Guide en /mux/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

mux_bp = Blueprint("mux", __name__, url_prefix="/mux")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "mux"

_legacy_ux_bp = Blueprint("ux_legacy", __name__, url_prefix="/ux")


@mux_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@mux_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@mux_bp.route("/personas/<path:filename>")
def personas(filename: str):
    persona_dir = _ROOT / "personas"
    target = (persona_dir / filename).resolve()
    if not str(target).startswith(str(persona_dir.resolve())):
        abort(404)
    return send_from_directory(persona_dir, filename)


@mux_bp.route("/journeys/<path:filename>")
def journeys(filename: str):
    journey_dir = _ROOT / "journeys"
    target = (journey_dir / filename).resolve()
    if not str(target).startswith(str(journey_dir.resolve())):
        abort(404)
    return send_from_directory(journey_dir, filename)


@mux_bp.route("/<path:filename>")
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


@mux_bp.route("")
def index_no_slash():
    return redirect(url_for("mux.index"))


@_legacy_ux_bp.route("/")
@_legacy_ux_bp.route("")
@_legacy_ux_bp.route("/<path:rest>")
def legacy_ux(rest: str = ""):
    suffix = rest.rstrip("/")
    dest = url_for("mux.index") if not suffix else f"/mux/{suffix}"
    return redirect(dest, code=301)
