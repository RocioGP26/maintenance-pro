"""Endpoints de salud para Render, UptimeRobot y balanceadores."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Blueprint, jsonify
from sqlalchemy import text

from app import db

health_bp = Blueprint("health", __name__)


def _check_database() -> tuple[bool, str | None]:
    try:
        db.session.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:
        return False, str(exc)


def _migration_revision() -> tuple[str | None, str | None]:
    try:
        revision = db.session.execute(
            text("SELECT version_num FROM alembic_version LIMIT 1")
        ).scalar()
        if revision:
            return str(revision), None
        return None, "alembic_version vacía"
    except Exception as exc:
        return None, str(exc)


@health_bp.get("/health/live")
def live():
    """Liveness: la app responde (sin tocar la BD)."""
    return jsonify({"status": "ok", "check": "live"}), 200


@health_bp.get("/health")
@health_bp.get("/health/ready")
def ready():
    """Readiness: BD accesible y migraciones aplicadas."""
    db_ok, db_error = _check_database()
    migration, migration_error = _migration_revision()

    payload = {
        "status": "ok" if db_ok and migration else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": os.environ.get("APP_VERSION", "dev"),
        "checks": {
            "database": {"ok": db_ok, "error": db_error},
            "migrations": {"ok": bool(migration), "revision": migration, "error": migration_error},
        },
    }

    if db_ok and migration:
        return jsonify(payload), 200
    return jsonify(payload), 503
