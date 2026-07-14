"""Logging estructurado para Maintix."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

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
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(app) -> None:
    level_name = app.config.get("LOG_LEVEL", "INFO")
    level = getattr(logging, level_name, logging.INFO)
    use_json = bool(app.config.get("LOG_JSON"))

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
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
        "Maintix v%s iniciando (build=%s, level=%s, json=%s)",
        __version__,
        build_commit or "local",
        level_name,
        use_json,
        extra={"app_version": __version__, "build_commit": build_commit or "local"},
    )
