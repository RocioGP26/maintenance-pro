"""Estado operativo de infraestructura para el panel SuperAdmin."""

from __future__ import annotations

import os
import smtplib
import ssl
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from flask import current_app
from sqlalchemy import text

from app import db


def check_database() -> tuple[bool, str | None, float]:
    started = time.perf_counter()
    try:
        db.session.execute(text("SELECT 1"))
        return True, None, round((time.perf_counter() - started) * 1000, 2)
    except Exception as exc:
        return False, type(exc).__name__, round((time.perf_counter() - started) * 1000, 2)


def migration_revision() -> tuple[str | None, str | None]:
    try:
        revision = db.session.execute(
            text("SELECT version_num FROM alembic_version LIMIT 1")
        ).scalar()
        if revision:
            return str(revision), None
        return None, "alembic_version vacía"
    except Exception as exc:
        return None, str(exc)


def _status_card(
    *,
    key: str,
    label: str,
    status: str,
    status_label: str,
    detail: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "status": status,  # ok | warn | error | unknown
        "status_label": status_label,
        "ok": status == "ok",
        "warn": status == "warn",
        "error": status == "error",
        "detail": detail,
        **extra,
    }


def smtp_status(*, probe: bool = True) -> dict[str, Any]:
    """Configuración SMTP y, opcionalmente, login de prueba (sin enviar correo)."""
    suppress = bool(current_app.config.get("MAIL_SUPPRESS_SEND"))
    server = (current_app.config.get("MAIL_SERVER") or "").strip()
    username = (current_app.config.get("MAIL_USERNAME") or "").strip()
    password = current_app.config.get("MAIL_PASSWORD") or ""
    sender = (
        current_app.config.get("MAIL_DEFAULT_SENDER")
        or current_app.config.get("MAIL_USERNAME")
        or ""
    ).strip()
    port = int(current_app.config.get("MAIL_PORT", 587) or 587)
    configured = bool(server and username and password and sender)
    label = "SMTP"

    if suppress:
        return _status_card(
            key="smtp",
            label=label,
            status="warn",
            status_label="Suprimido",
            detail="El envío de correo está desactivado en este entorno (modo prueba).",
            configured=configured,
            server=server or None,
        )
    if not configured:
        missing = [
            name
            for name, value in (
                ("servidor", server),
                ("usuario", username),
                ("contraseña", password),
                ("remitente", sender),
            )
            if not value
        ]
        return _status_card(
            key="smtp",
            label=label,
            status="error",
            status_label="No configurado",
            detail="Falta configurar: " + ", ".join(missing) + ".",
            configured=False,
            server=None,
        )

    if not probe:
        return _status_card(
            key="smtp",
            label=label,
            status="ok",
            status_label="Configurado",
            detail=f"{server}:{port} · remitente {sender}",
            configured=True,
            server=server,
        )

    started = time.perf_counter()
    try:
        with smtplib.SMTP(
            server,
            port,
            timeout=int(current_app.config.get("MAIL_TIMEOUT_SECONDS", 8) or 8),
        ) as smtp:
            smtp.ehlo()
            if current_app.config.get("MAIL_USE_TLS", True):
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
            smtp.login(username, password)
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return _status_card(
            key="smtp",
            label=label,
            status="ok",
            status_label="Operativo",
            detail=f"{server}:{port} · autenticación correcta ({int(round(latency_ms))} ms)",
            configured=True,
            server=server,
            latency_ms=latency_ms,
        )
    except (OSError, smtplib.SMTPException):
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return _status_card(
            key="smtp",
            label=label,
            status="error",
            status_label="Fallido",
            detail=f"No se pudo autenticar en {server}:{port}.",
            configured=True,
            server=server,
            latency_ms=latency_ms,
        )


def _backup_dir() -> Path:
    return Path(os.environ.get("BACKUP_DIR", "backups"))


def _latest_local_backup() -> Optional[tuple[Path, float]]:
    root = _backup_dir()
    if not root.is_dir():
        return None
    newest: Optional[Path] = None
    newest_mtime = 0.0
    for path in root.iterdir():
        if not path.is_file():
            continue
        try:
            mtime = path.stat().st_mtime
        except OSError:
            continue
        if mtime >= newest_mtime:
            newest = path
            newest_mtime = mtime
    if newest is None:
        return None
    return newest, newest_mtime


def backups_status() -> dict[str, Any]:
    """Config de backup S3 + último artefacto local en BACKUP_DIR."""
    from app.storage_backup import StorageBackupConfig

    label = "Backups"
    storage_ok = False
    storage_detail = "Falta configurar el bucket de recuperación y sus credenciales."
    try:
        cfg = StorageBackupConfig.from_environment()
        cfg.validate()
        storage_ok = True
        storage_detail = f"Bucket de recuperación: {cfg.target_bucket}"
    except ValueError:
        pass

    latest = _latest_local_backup()
    max_age_h = max(1, int(os.environ.get("BACKUP_STALE_HOURS", "36") or 36))
    local_detail = "No hay copias locales en este servidor."
    age_hours: Optional[float] = None
    local_name: Optional[str] = None
    if latest:
        path, mtime = latest
        local_name = path.name
        age_hours = max(0.0, (time.time() - mtime) / 3600.0)
        when = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        local_detail = f"Última copia local: {local_name} · {when} ({age_hours:.1f} h)"

    if storage_ok and latest and age_hours is not None and age_hours <= max_age_h:
        status, status_label = "ok", "Al día"
        detail = f"{storage_detail}. {local_detail}."
    elif storage_ok and latest:
        status, status_label = "warn", "Antiguo"
        detail = f"{storage_detail}. {local_detail} · umbral {max_age_h} h."
    elif storage_ok:
        status, status_label = "warn", "Sin copia local"
        detail = (
            f"{storage_detail}. {local_detail} "
            "Los respaldos diarios se guardan en el bucket de recuperación (GitHub Actions)."
        )
    elif latest and age_hours is not None and age_hours <= max_age_h:
        status, status_label = "warn", "Solo local"
        detail = f"{local_detail}. Aún falta el bucket de recuperación."
    else:
        status, status_label = "error", "Sin respaldo"
        detail = f"{storage_detail} {local_detail}"

    return _status_card(
        key="backups",
        label=label,
        status=status,
        status_label=status_label,
        detail=detail,
        storage_configured=storage_ok,
        local_name=local_name,
        age_hours=round(age_hours, 1) if age_hours is not None else None,
    )


def workers_status() -> dict[str, Any]:
    redis_configured = bool((current_app.config.get("REDIS_URL") or "").strip())
    worker_required = bool(current_app.config.get("WORKER_HEARTBEAT_REQUIRED"))
    worker_max_age = max(
        10, int(current_app.config.get("WORKER_HEARTBEAT_MAX_AGE_SECONDS", 90) or 90)
    )
    label = "Workers"

    if not redis_configured:
        status = "error" if worker_required else "warn"
        return _status_card(
            key="workers",
            label=label,
            status=status,
            status_label="Sin Redis",
            detail="Redis no está configurado; no se puede verificar el worker.",
            required=worker_required,
            heartbeat_age_seconds=None,
        )

    from app.redis_client import check_redis, worker_heartbeat_age

    redis_ok, redis_error, redis_ms = check_redis()
    if not redis_ok:
        return _status_card(
            key="workers",
            label=label,
            status="error",
            status_label="Redis caído",
            detail="No se pudo conectar a Redis.",
            required=worker_required,
            heartbeat_age_seconds=None,
            redis_latency_ms=redis_ms,
            redis_error=redis_error,
        )

    try:
        age = worker_heartbeat_age()
    except Exception as exc:
        return _status_card(
            key="workers",
            label=label,
            status="error",
            status_label="Error",
            detail="No se pudo leer el heartbeat del worker.",
            required=worker_required,
            heartbeat_age_seconds=None,
            error=type(exc).__name__,
        )

    if age is not None and age <= worker_max_age:
        return _status_card(
            key="workers",
            label=label,
            status="ok",
            status_label="Activo",
            detail=f"Último latido hace {age:.0f} s (límite {worker_max_age} s).",
            required=worker_required,
            heartbeat_age_seconds=round(age, 2),
            redis_latency_ms=redis_ms,
        )

    if worker_required:
        detail = (
            "El worker no ha reportado latido recientemente."
            if age is None
            else f"Último latido hace {age:.0f} s (límite {worker_max_age} s)."
        )
        return _status_card(
            key="workers",
            label=label,
            status="error",
            status_label="Sin latido",
            detail=detail,
            required=True,
            heartbeat_age_seconds=round(age, 2) if age is not None else None,
            redis_latency_ms=redis_ms,
        )

    return _status_card(
        key="workers",
        label=label,
        status="warn",
        status_label="Opcional",
        detail=(
            "El worker no es obligatorio en este entorno."
            if age is None
            else f"Último latido hace {age:.0f} s (no obligatorio)."
        ),
        required=False,
        heartbeat_age_seconds=round(age, 2) if age is not None else None,
        redis_latency_ms=redis_ms,
    )


def health_status() -> dict[str, Any]:
    """Resumen del readiness (sin emitir alertas operativas)."""
    db_ok, db_error, db_latency_ms = check_database()
    migration, migration_error = migration_revision()
    degraded_threshold = max(1, int(current_app.config.get("DB_HEALTH_DEGRADED_MS", 750) or 750))
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

    worker_required = bool(current_app.config.get("WORKER_HEARTBEAT_REQUIRED"))
    worker_max_age = max(
        10, int(current_app.config.get("WORKER_HEARTBEAT_MAX_AGE_SECONDS", 90) or 90)
    )
    worker_ok = (
        not worker_required
        or (redis_ok and worker_age is not None and worker_age <= worker_max_age)
    )
    ready_ok = db_ok and bool(migration) and (redis_ok or not redis_required)
    redis_threshold = max(1, int(current_app.config.get("REDIS_HEALTH_DEGRADED_MS", 250) or 250))
    redis_degraded = redis_ok and redis_configured and redis_latency_ms >= redis_threshold

    if not ready_ok:
        status, status_label = "error", "No listo"
    elif db_degraded or redis_degraded or not worker_ok:
        status, status_label = "warn", "Degradado"
    else:
        status, status_label = "ok", "Saludable"

    def _ok(flag: bool) -> str:
        return "ok" if flag else "fallo"

    parts = [
        f"Base de datos {_ok(db_ok)} ({int(round(db_latency_ms))} ms)",
        f"migraciones {_ok(bool(migration))}",
    ]
    if redis_configured or redis_required:
        parts.append(f"Redis {_ok(redis_ok)}")
    if worker_required:
        parts.append(f"worker {_ok(worker_ok)}")

    return _status_card(
        key="health",
        label="Health check",
        status=status,
        status_label=status_label,
        detail=" · ".join(parts),
        ready=ready_ok,
        endpoint="/health/ready",
        checks={
            "database_ok": db_ok,
            "database_degraded": db_degraded,
            "migrations_ok": bool(migration),
            "migration": migration,
            "redis_ok": redis_ok,
            "worker_ok": worker_ok,
            "database_error": db_error,
            "migration_error": migration_error,
            "redis_error": redis_error,
        },
    )


def service_statuses(*, probe_smtp: bool = True) -> list[dict[str, Any]]:
    return [
        smtp_status(probe=probe_smtp),
        backups_status(),
        workers_status(),
        health_status(),
    ]
