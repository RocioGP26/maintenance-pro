"""Cliente compartido para Redis/Render Key Value."""

from __future__ import annotations

import time

from flask import current_app


WORKER_HEARTBEAT_KEY = "roustix:worker:heartbeat"


def get_redis():
    """Devuelve un cliente por aplicación y valida que exista REDIS_URL."""
    client = current_app.extensions.get("roustix_redis")
    if client is not None:
        return client
    url = (current_app.config.get("REDIS_URL") or "").strip()
    if not url:
        raise RuntimeError("REDIS_URL no está configurada.")
    import redis

    client = redis.Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
    )
    current_app.extensions["roustix_redis"] = client
    return client


def check_redis() -> tuple[bool, str | None, float]:
    started = time.perf_counter()
    try:
        get_redis().ping()
        return True, None, round((time.perf_counter() - started) * 1000, 2)
    except Exception as exc:
        return False, type(exc).__name__, round((time.perf_counter() - started) * 1000, 2)


def publish_worker_heartbeat(*, ttl_seconds: int) -> None:
    ttl = max(10, int(ttl_seconds))
    get_redis().set(WORKER_HEARTBEAT_KEY, str(time.time()), ex=ttl)


def worker_heartbeat_age() -> float | None:
    value = get_redis().get(WORKER_HEARTBEAT_KEY)
    if value is None:
        return None
    try:
        return max(0.0, time.time() - float(value))
    except (TypeError, ValueError):
        return None
