"""Sirve MKT (docs/mkt/) — Sales Enablement & Marketing Assets en /mkt/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

mkt_bp = Blueprint("mkt", __name__, url_prefix="/mkt")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "mkt"


@mkt_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@mkt_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@mkt_bp.route("/chapters/<path:filename>")
def chapters(filename: str):
    ch_dir = _ROOT / "chapters"
    target = (ch_dir / filename).resolve()
    if not str(target).startswith(str(ch_dir.resolve())):
        abort(404)
    return send_from_directory(ch_dir, filename)


@mkt_bp.route("/assets/<path:filename>")
def assets(filename: str):
    assets_dir = _ROOT / "assets"
    target = (assets_dir / filename).resolve()
    if not str(target).startswith(str(assets_dir.resolve())):
        abort(404)
    return send_from_directory(assets_dir, filename)


@mkt_bp.route("/mtx-case/<path:filename>")
def mtx_case(filename: str):
    case_dir = _ROOT / "mtx-case"
    target = (case_dir / filename).resolve()
    if not str(target).startswith(str(case_dir.resolve())):
        abort(404)
    if filename.endswith(".md"):
        return send_from_directory(case_dir, filename, mimetype="text/markdown; charset=utf-8")
    return send_from_directory(case_dir, filename)


@mkt_bp.route("/<path:filename>")
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


@mkt_bp.route("")
def index_no_slash():
    return redirect(url_for("mkt.index"))
