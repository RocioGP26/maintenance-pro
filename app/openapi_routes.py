"""Sirve la especificación OpenAPI v1 — MSD-03."""

from __future__ import annotations

from pathlib import Path

import yaml
from flask import Blueprint, Response, jsonify

openapi_bp = Blueprint("openapi", __name__)

_SPEC_PATH = Path(__file__).resolve().parent.parent / "docs" / "api" / "openapi.v1.yaml"


def _load_spec() -> dict:
    with _SPEC_PATH.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


@openapi_bp.route("/api/v1/openapi.json")
def openapi_json():
    return jsonify(_load_spec())


@openapi_bp.route("/api/v1/openapi.yaml")
def openapi_yaml():
    return Response(
        _SPEC_PATH.read_text(encoding="utf-8"),
        mimetype="text/yaml; charset=utf-8",
    )
