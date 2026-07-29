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

    if suppress:
        return _status_card(
            key="smtp",
            label="Estado SMTP",
            status="warn",
            status_label="Suprimido",
            detail="MAIL_SUPPRESS_SEND activo · los correos no salen (modo prueba).",
            configured=configured,
            server=server or None,
        )
    if not configured:
        missing = [
            name
            for name, value in (
                ("MAIL_SERVER", server),
                ("MAIL_USERNAME", username),
                ("MAIL_PASSWORD", password),
                ("MAIL_DEFAULT_SENDER", sender),
            )
            if not value
        ]
        return _status_card(
            key="smtp",
            label="Estado SMTP",
            status="error",
            status_label="No configurado",
            detail="Faltan: " + ", ".join(missing),
            configured=False,
            server=None,
        )

    if not probe:
        return _status_card(
            key="smtp",
            label="Estado SMTP",
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
            label="Estado SMTP",
            status="ok",
            status_label="Operativo",
            detail=f"{server}:{port} · login OK ({latency_ms} ms)",
            configured=True,
            server=server,
            latency_ms=latency_ms,
        )
    except (OSError, smtplib.SMTPException) as exc:
        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        return _status_card(
            key="smtp",
            label="Estado SMTP",
            status="error",
            status_label="Fallido",
            detail=f"No se pudo autenticar en {server}:{port} ({type(exc).__name__})",
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

    storage_ok = False
    storage_detail = "STORAGE_BACKUP_* incompleto"
    try:
        cfg = StorageBackupConfig.from_environment()
        cfg.validate()
        storage_ok = True
        storage_detail = f"Bucket recuperación: {cfg.target_bucket}"
    except ValueError as exc:
        storage_detail = str(exc)

    latest = _latest_local_backup()
    max_age_h = max(1, int(os.environ.get("BACKUP_STALE_HOURS", "36") or 36))
    local_detail = "Sin archivos en BACKUP_DIR"
    age_hours: Optional[float] = None
    local_name: Optional[str] = None
    if latest:
        path, mtime = latest
        local_name = path.name
        age_hours = max(0.0, (time.time() - mtime) / 3600.0)
        when = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        local_detail = f"Último local: {local_name} · {when} ({age_hours:.1f} h)"

    if storage_ok and latest and age_hours is not None and age_hours <= max_age_h:
        status, label = "ok", "Al día"
        detail = f"{storage_detail}. {local_detail}"
    elif storage_ok and latest:
        status, label = "warn", "Antiguo"
        detail = f"{storage_detail}. {local_detail} · umbral {max_age_h} h"
    elif storage_ok:
        status, label = "warn", "Sin local reciente"
        detail = (
            f"{storage_detail}. {local_detail}. "
            "Los dumps diarios viven en el bucket de recuperación (GitHub Actions)."
        )
    elif latest and age_hours is not None and age_hours <= max_age_h:
        status, label = "warn", "Solo local"
        detail = f"{local_detail}. Config S3 de recuperación incompleta."
    else:
        status, label = "error", "Sin respaldo"
        detail = f"{storage_detail}. {local_detail}"

    return _status_card(
        key="backups",
        label="Estado Backups",
        status=status,
        status_label=label,
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

    if not redis_configured:
        status = "error" if worker_required else "warn"
        return _status_card(
            key="workers",
            label="Estado Workers",
            status=status,
            status_label="Sin Redis",
            detail="REDIS_URL no configurada · no hay heartbeat de worker.",
            required=worker_required,
            heartbeat_age_seconds=None,
        )

    from app.redis_client import check_redis, worker_heartbeat_age

    redis_ok, redis_error, redis_ms = check_redis()
    if not redis_ok:
        return _status_card(
            key="workers",
            label="Estado Workers",
            status="error",
            status_label="Redis caído",
            detail=f"No se pudo hacer ping a Redis ({redis_error})",
            required=worker_required,
            heartbeat_age_seconds=None,
            redis_latency_ms=redis_ms,
        )

    try:
        age = worker_heartbeat_age()
    except Exception as exc:
        return _status_card(
            key="workers",
            label="Estado Workers",
            status="error",
            status_label="Error heartbeat",
            detail=type(exc).__name__,
            required=worker_required,
            heartbeat_age_seconds=None,
        )

    if age is not None and age <= worker_max_age:
        return _status_card(
            key="workers",
            label="Estado Workers",
            status="ok",
            status_label="Activo",
            detail=f"Heartbeat hace {age:.0f} s · límite {worker_max_age} s",
            required=worker_required,
            heartbeat_age_seconds=round(age, 2),
            redis_latency_ms=redis_ms,
        )

    if worker_required:
        detail = (
            "Heartbeat ausente o caducado."
            if age is None
            else f"Heartbeat hace {age:.0f} s · límite {worker_max_age} s"
        )
        return _status_card(
            key="workers",
            label="Estado Workers",
            status="error",
            status_label="Sin heartbeat",
            detail=detail,
            required=True,
            heartbeat_age_seconds=round(age, 2) if age is not None else None,
            redis_latency_ms=redis_ms,
        )

    return _status_card(
        key="workers",
        label="Estado Workers",
        status="warn",
        status_label="Opcional",
        detail=(
            "Worker no requerido en este entorno."
            if age is None
            else f"Heartbeat hace {age:.0f} s (no obligatorio)."
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
        status, label = "error", "No listo"
    elif db_degraded or redis_degraded or not worker_ok:
        status, label = "warn", "Degradado"
    else:
        status, label = "ok", "Saludable"

    parts = [
        f"BD {'OK' if db_ok else 'FAIL'} ({db_latency_ms} ms)",
        f"migraciones {'OK' if migration else 'FAIL'}",
    ]
    if redis_configured or redis_required:
        parts.append(f"Redis {'OK' if redis_ok else 'FAIL'}")
    if worker_required:
        parts.append(f"worker {'OK' if worker_ok else 'FAIL'}")
    if db_error:
        parts.append(db_error)
    if migration_error and not migration:
        parts.append(migration_error)
    if redis_error and not redis_ok:
        parts.append(str(redis_error))

    return _status_card(
        key="health",
        label="Estado Health Check",
        status=status,
        status_label=label,
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
        },
    )


def service_statuses(*, probe_smtp: bool = True) -> list[dict[str, Any]]:
    return [
        smtp_status(probe=probe_smtp),
        backups_status(),
        workers_status(),
        health_status(),
    ]
