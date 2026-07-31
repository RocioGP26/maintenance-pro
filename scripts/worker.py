"""Worker continuo de Roustix para outbox y tareas periódicas."""

from __future__ import annotations

import logging
import signal
import threading
import time

from app import create_app, db
from app.email_service import process_pending_emails
from app.integrations.webhooks import process_pending_deliveries
from app.observability import emit_operational_alert
from app.redis_client import get_redis, publish_worker_heartbeat
from app.startup import run_maintenance_tasks


logger = logging.getLogger("app.worker")
MAINTENANCE_LOCK_KEY = "roustix:worker:maintenance-lock"


def process_worker_cycle(*, run_maintenance: bool = False) -> dict:
    """Ejecuta un ciclo determinista; se expone para pruebas y one-off jobs."""
    app = create_app("worker")
    with app.app_context():
        poll_seconds = max(0.25, float(app.config.get("WORKER_POLL_SECONDS", 2.0)))
        heartbeat_ttl = max(30, int(poll_seconds * 5))
        publish_worker_heartbeat(ttl_seconds=heartbeat_ttl)
        stats = process_pending_deliveries(
            limit=max(1, int(app.config.get("WORKER_WEBHOOK_BATCH_SIZE", 50)))
        )
        stats.update(
            process_pending_emails(
                limit=max(1, int(app.config.get("WORKER_EMAIL_BATCH_SIZE", 50)))
            )
        )
        if run_maintenance:
            stats["maintenance"] = _run_maintenance_with_lock(app)
        return stats


def _run_maintenance_with_lock(app) -> bool:
    timeout = max(60, int(app.config.get("WORKER_MAINTENANCE_INTERVAL_SECONDS", 3600)))
    lock = get_redis().lock(
        MAINTENANCE_LOCK_KEY,
        timeout=timeout,
        blocking=False,
    )
    if not lock.acquire(blocking=False):
        return False
    try:
        run_maintenance_tasks()
        return True
    finally:
        try:
            lock.release()
        except Exception:
            logger.warning(
                "Worker maintenance lock was no longer owned",
                extra={"component": "worker", "event": "maintenance_lock_lost"},
            )


def run_forever() -> None:
    app = create_app("worker")
    stop = threading.Event()

    def _stop(_signum, _frame):
        stop.set()

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    poll_seconds = max(0.25, float(app.config.get("WORKER_POLL_SECONDS", 2.0)))
    batch_size = max(1, int(app.config.get("WORKER_WEBHOOK_BATCH_SIZE", 50)))
    email_batch_size = max(1, int(app.config.get("WORKER_EMAIL_BATCH_SIZE", 50)))
    maintenance_enabled = bool(app.config.get("WORKER_MAINTENANCE_ENABLED"))
    maintenance_interval = max(
        60, int(app.config.get("WORKER_MAINTENANCE_INTERVAL_SECONDS", 3600))
    )
    heartbeat_ttl = max(30, int(poll_seconds * 5))
    next_maintenance = time.monotonic()

    with app.app_context():
        get_redis().ping()
    logger.info(
        "Roustix worker started",
        extra={"component": "worker", "event": "worker_started"},
    )

    while not stop.is_set():
        started = time.monotonic()
        try:
            with app.app_context():
                publish_worker_heartbeat(ttl_seconds=heartbeat_ttl)
                stats = process_pending_deliveries(limit=batch_size)
                stats.update(process_pending_emails(limit=email_batch_size))
                if maintenance_enabled and started >= next_maintenance:
                    stats["maintenance"] = _run_maintenance_with_lock(app)
                    next_maintenance = started + maintenance_interval
                logger.info(
                    "Worker cycle completed",
                    extra={
                        "component": "worker",
                        "event": "worker_cycle_completed",
                        **{key: stats.get(key, 0) for key in (
                            "recovered", "claimed", "delivered", "failed", "retry",
                            "email_recovered", "email_claimed", "email_sent",
                            "email_failed", "email_retry",
                        )},
                    },
                )
        except Exception as exc:
            with app.app_context():
                db.session.rollback()
                emit_operational_alert(
                    "worker",
                    "cycle_failed",
                    "Worker cycle failed",
                    exc=exc,
                    dedupe_key=f"worker:cycle:{type(exc).__name__}",
                )
        finally:
            with app.app_context():
                db.session.remove()
        elapsed = time.monotonic() - started
        stop.wait(max(0.05, poll_seconds - elapsed))

    logger.info(
        "Roustix worker stopped",
        extra={"component": "worker", "event": "worker_stopped"},
    )


if __name__ == "__main__":
    run_forever()
