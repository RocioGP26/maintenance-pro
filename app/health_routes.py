"""Endpoints de salud para Render, UptimeRobot y balanceadores."""

from __future__ import annotations

from datetime import datetime, timezone
import time

from flask import Blueprint, current_app, jsonify
from sqlalchemy import text

from app import db
from app.observability import emit_operational_alert
from app.version import __version__, get_version_info

health_bp = Blueprint("health", __name__)


@health_bp.get("/version")
@health_bp.get("/api/v1/version")
def version():
    """Versión pública segura de la aplicación y del build desplegado."""
    response = jsonify(get_version_info())
    response.headers["Cache-Control"] = "no-store"
    return response, 200


def _check_database() -> tuple[bool, str | None, float]:
    started = time.perf_counter()
    try:
        db.session.execute(text("SELECT 1"))
        return True, None, round((time.perf_counter() - started) * 1000, 2)
    except Exception as exc:
        return False, type(exc).__name__, round((time.perf_counter() - started) * 1000, 2)


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
    db_ok, db_error, db_latency_ms = _check_database()
    migration, migration_error = _migration_revision()
    degraded_threshold = max(1, int(current_app.config.get("DB_HEALTH_DEGRADED_MS", 750)))
    db_degraded = db_ok and db_latency_ms >= degraded_threshold
    redis_required = bool(current_app.config.get("DISTRIBUTED_RATE_LIMITS_REQUIRED"))
    redis_configured = bool((current_app.config.get("REDIS_URL") or "").strip())
    redis_ok, redis_error, redis_latency_ms = True, None, 0.0
    worker_age = None
    if redis_configured:
        from app.redis_client import check_redis, worker_heartbeat_age

        redis_ok, redis_error, redis_latency_ms = check_redis()
        if redis_ok and current_app.config.get("WORKER_HEARTBEAT_REQUIRED"):
            try:
                worker_age = worker_heartbeat_age()
            except Exception as exc:
                redis_ok = False
                redis_error = type(exc).__name__
    elif redis_required:
        redis_ok, redis_error = False, "not_configured"

    redis_threshold = max(1, int(current_app.config.get("REDIS_HEALTH_DEGRADED_MS", 250)))
    redis_degraded = redis_ok and redis_configured and redis_latency_ms >= redis_threshold
    worker_required = bool(current_app.config.get("WORKER_HEARTBEAT_REQUIRED"))
    worker_max_age = max(
        10, int(current_app.config.get("WORKER_HEARTBEAT_MAX_AGE_SECONDS", 90))
    )
    worker_ok = (
        not worker_required
        or (redis_ok and worker_age is not None and worker_age <= worker_max_age)
    )
    ready_ok = db_ok and bool(migration) and (redis_ok or not redis_required)

    payload = {
        "status": "degraded" if any((db_degraded, redis_degraded, not worker_ok, not ready_ok)) else "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": __version__,
        "checks": {
            "database": {
                "ok": db_ok,
                "degraded": db_degraded,
                "latency_ms": db_latency_ms,
                "error": db_error,
            },
            "migrations": {"ok": bool(migration), "revision": migration, "error": migration_error},
            "redis": {
                "ok": redis_ok,
                "required": redis_required,
                "configured": redis_configured,
                "degraded": redis_degraded,
                "latency_ms": redis_latency_ms,
                "error": redis_error,
            },
            "worker": {
                "ok": worker_ok,
                "required": worker_required,
                "heartbeat_age_seconds": round(worker_age, 2) if worker_age is not None else None,
                "max_age_seconds": worker_max_age,
            },
        },
    }

    if not db_ok:
        emit_operational_alert(
            "database", "unavailable", "Database readiness check failed",
            context={"status_code": 503},
        )
    elif not migration:
        emit_operational_alert(
            "database", "migration_missing", "Database migration revision is unavailable",
            context={"status_code": 503},
        )
    elif db_degraded:
        emit_operational_alert(
            "database", "degraded", "Database latency exceeded the readiness threshold",
            severity="warning",
            context={"status_code": 200},
        )
    if not redis_ok:
        emit_operational_alert(
            "redis", "unavailable", "Redis readiness check failed",
            context={"status_code": 503 if redis_required else 200},
        )
    elif redis_degraded:
        emit_operational_alert(
            "redis", "degraded", "Redis latency exceeded the readiness threshold",
            severity="warning",
            context={"status_code": 200},
        )
    if not worker_ok:
        emit_operational_alert(
            "worker", "heartbeat_stale", "Worker heartbeat is missing or stale",
            context={"status_code": 200},
        )

    return jsonify(payload), 200 if ready_ok else 503
