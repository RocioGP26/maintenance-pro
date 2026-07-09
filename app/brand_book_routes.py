"""Sirve el Brand Book v2.0 (docs/brandbook/) en /brandbook/."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, abort, redirect, send_from_directory, url_for

brand_book_bp = Blueprint("brand_book", __name__, url_prefix="/brandbook")

_ROOT = Path(__file__).resolve().parent.parent / "docs" / "brandbook"

# Compatibilidad con rutas anteriores
_legacy_bp = Blueprint("brand_book_legacy", __name__, url_prefix="/brand-book")


@brand_book_bp.route("/")
def index():
    return send_from_directory(_ROOT, "index.html")


@brand_book_bp.route("/css/<path:filename>")
def css(filename: str):
    css_dir = _ROOT / "css"
    target = (css_dir / filename).resolve()
    if not str(target).startswith(str(css_dir.resolve())):
        abort(404)
    return send_from_directory(css_dir, filename)


@brand_book_bp.route("/assets/<path:filename>")
def assets(filename: str):
    assets_dir = _ROOT / "assets"
    target = (assets_dir / filename).resolve()
    if not str(target).startswith(str(assets_dir.resolve())):
        abort(404)
    return send_from_directory(assets_dir, filename)


@brand_book_bp.route("")
def index_no_slash():
    return redirect(url_for("brand_book.index"))


@_legacy_bp.route("/")
@_legacy_bp.route("")
def legacy_index():
    return redirect(url_for("brand_book.index"), code=301)


@_legacy_bp.route("/mdl")
@_legacy_bp.route("/mdl.html")
def legacy_mdl():
    return redirect(url_for("mdl.index"), code=301)


@_legacy_bp.route("/css/<path:filename>")
def legacy_css(filename: str):
    return redirect(f"/brandbook/css/{filename}", code=301)


@_legacy_bp.route("/assets/<path:filename>")
def legacy_assets(filename: str):
    return redirect(f"/brandbook/assets/{filename}", code=301)
