"""Logging estructurado para Roustix."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from flask import g, has_request_context, request
from flask_login import current_user

from app.version import __version__, get_build_commit


class JsonFormatter(logging.Formatter):
    """Emite cada registro como una línea JSON (ideal para producción / agregadores)."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key in (
            "request_id",
            "empresa_id",
            "user_id",
            "path",
            "method",
            "status_code",
            "app_version",
            "build_commit",
            "endpoint",
            "duration_ms",
            "component",
            "event",
            "severity",
            "error_type",
            "endpoint_id",
            "delivery_id",
            "claimed",
            "delivered",
            "failed",
            "retry",
            "recovered",
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


class RequestContextFilter(logging.Filter):
    """Añade correlación y tenant a cualquier log emitido durante una petición."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not has_request_context():
            return True
        if not hasattr(record, "request_id"):
            record.request_id = getattr(g, "request_id", None)
        if not hasattr(record, "path"):
            record.path = request.path
        if not hasattr(record, "method"):
            record.method = request.method
        if not hasattr(record, "endpoint"):
            record.endpoint = request.endpoint or "unmatched"
        try:
            if current_user.is_authenticated:
                if not hasattr(record, "user_id"):
                    record.user_id = getattr(current_user, "id", None)
                if not hasattr(record, "empresa_id"):
                    record.empresa_id = getattr(current_user, "empresa_id", None)
        except Exception:
            pass
        return True


def setup_logging(app) -> None:
    level_name = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name, logging.INFO)
    use_json = bool(app.config.get("LOG_JSON"))

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestContextFilter())
    if use_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    root.addHandler(handler)

    for noisy in ("werkzeug", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    build_commit = get_build_commit()
    app.logger.info(
        "Roustix v%s iniciando (build=%s, level=%s, json=%s)",
        __version__,
        build_commit or "local",
        level_name,
        use_json,
        extra={"app_version": __version__, "build_commit": build_commit or "local"},
    )
