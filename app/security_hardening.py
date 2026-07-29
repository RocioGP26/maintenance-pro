"""Controles de configuración y perímetro para ejecución productiva."""

from __future__ import annotations

import os
from collections.abc import Mapping
from urllib.parse import urlparse

from flask import abort, request
from werkzeug.middleware.proxy_fix import ProxyFix


def _value(config: Mapping, name: str) -> str:
    return str(config.get(name, "") or "").strip()


def _weak_secret(value: str) -> bool:
    normalized = (value or "").strip().lower()
    markers = ("cambia-esto", "change-me", "changeme", "tu-clave", "dev-secret")
    return len(value) < 32 or len(set(value)) < 8 or any(marker in normalized for marker in markers)


def _valid_totp_secret(value: str) -> bool:
    if not value:
        return False
    try:
        import pyotp

        pyotp.TOTP(value).at(0)
        return True
    except Exception:
        return False


def production_configuration_errors(config: Mapping) -> list[str]:
    """Devuelve errores que hacen inseguro o no persistente un despliegue."""
    errors: list[str] = []
    secret = _value(config, "SECRET_KEY")
    if _weak_secret(secret):
        errors.append("SECRET_KEY debe ser aleatoria y contener al menos 32 caracteres.")

    database_url = _value(config, "SQLALCHEMY_DATABASE_URI").lower()
    if not database_url.startswith(("postgresql://", "postgresql+psycopg://")):
        errors.append("DATABASE_URL debe usar PostgreSQL en producción.")

    if _value(config, "STORAGE_BACKEND").lower() != "s3":
        errors.append("STORAGE_BACKEND debe ser s3 en producción.")
    for key in (
        "STORAGE_BUCKET",
        "STORAGE_ENDPOINT_URL",
        "STORAGE_ACCESS_KEY_ID",
        "STORAGE_SECRET_ACCESS_KEY",
    ):
        if not _value(config, key):
            errors.append(f"{key} es obligatoria en producción.")
    endpoint = _value(config, "STORAGE_ENDPOINT_URL")
    if endpoint and urlparse(endpoint).scheme != "https":
        errors.append("STORAGE_ENDPOINT_URL debe usar HTTPS.")

    if not bool(config.get("MAIL_SUPPRESS_SEND")):
        for key in ("MAIL_SERVER", "MAIL_USERNAME", "MAIL_PASSWORD", "MAIL_DEFAULT_SENDER"):
            if not _value(config, key):
                errors.append(f"{key} es obligatoria para identidad en producción.")

    platform_key = _value(config, "PLATFORM_ADMIN_KEY")
    if platform_key and _weak_secret(platform_key):
        errors.append("PLATFORM_ADMIN_KEY debe ser aleatoria y contener al menos 32 caracteres.")
    if platform_key and bool(config.get("PLATFORM_MFA_REQUIRED", True)):
        if not _valid_totp_secret(_value(config, "PLATFORM_ADMIN_TOTP_SECRET")):
            errors.append(
                "PLATFORM_ADMIN_TOTP_SECRET válido es obligatorio cuando el panel de plataforma está habilitado."
            )
    if bool(config.get("DISTRIBUTED_RATE_LIMITS_REQUIRED")):
        redis_url = _value(config, "REDIS_URL").lower()
        if not redis_url.startswith(("redis://", "rediss://")):
            errors.append(
                "REDIS_URL debe usar Redis/Render Key Value para rate limiting distribuido."
            )
    return errors


def enforce_production_configuration(app) -> None:
    errors = production_configuration_errors(app.config)
    if errors:
        detail = "\n- ".join(errors)
        raise RuntimeError(f"Configuración productiva insegura:\n- {detail}")


def enforce_worker_configuration(app) -> None:
    """Evita iniciar un worker sin sus dependencias de coordinación."""
    errors: list[str] = []
    if _weak_secret(_value(app.config, "SECRET_KEY")):
        errors.append("SECRET_KEY debe ser aleatoria y contener al menos 32 caracteres.")
    database_url = _value(app.config, "SQLALCHEMY_DATABASE_URI").lower()
    if not database_url.startswith(("postgresql://", "postgresql+psycopg://")):
        errors.append("DATABASE_URL debe usar PostgreSQL para el worker.")
    redis_url = _value(app.config, "REDIS_URL").lower()
    if not redis_url.startswith(("redis://", "rediss://")):
        errors.append("REDIS_URL debe usar Redis/Render Key Value para el worker.")
    if errors:
        detail = "\n- ".join(errors)
        raise RuntimeError(f"Configuración insegura del worker:\n- {detail}")


def _allowed_hosts() -> frozenset[str]:
    configured = {
        item.strip().lower().rstrip(".")
        for item in os.environ.get("TRUSTED_HOSTS", "").split(",")
        if item.strip()
    }
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "").strip().lower().rstrip(".")
    if render_host:
        configured.add(render_host)
    return frozenset(configured)


def register_runtime_hardening(app, *, production: bool) -> None:
    """Configura el límite de confianza HTTP sin afectar desarrollo ni tests."""
    if not production:
        return
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    allowed = _allowed_hosts()
    if not allowed:
        return

    @app.before_request
    def _guard_host_header():
        host = (request.host or "").split(":", 1)[0].lower().rstrip(".")
        if host not in allowed:
            abort(400, description="Host no permitido.")
        return None
