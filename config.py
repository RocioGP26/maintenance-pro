"""Configuración por entorno (desarrollo, producción, pruebas)."""

from __future__ import annotations

import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

# Debe ejecutarse antes de construir las clases Config: sus atributos leen os.environ
# durante la importación del módulo.
load_dotenv()

from app.version import __version__

BASE_DIR = Path(__file__).resolve().parent


def normalize_database_url(url: str) -> str:
    raw = (url or "").strip()
    if raw.startswith("postgres://"):
        return raw.replace("postgres://", "postgresql+psycopg://", 1)
    if raw.startswith("postgresql://"):
        return raw.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw


def _default_sqlite_uri() -> str:
    return "sqlite:///" + str(BASE_DIR / "mantenimiento.db")


def _is_sqlite_uri(uri: str) -> bool:
    return (uri or "").strip().lower().startswith("sqlite:")


def sqlite_engine_options() -> dict:
    """SQLite local: más tolerante a lecturas concurrentes (Flask debug, DB Browser)."""
    return {
        "connect_args": {"timeout": 30},
        "pool_pre_ping": True,
    }


def engine_options_for(uri: str) -> dict:
    if _is_sqlite_uri(uri):
        return sqlite_engine_options()
    return {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


def _env_flag(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes")


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)).strip())
    except (TypeError, ValueError):
        return default


class Config:
    """Valores compartidos entre entornos."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    SESSION_REFRESH_EACH_REQUEST = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_VERSION = __version__

    # Correo transaccional. Gmail SMTP funciona con una contraseña de aplicación.
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com").strip()
    MAIL_PORT = _env_int("MAIL_PORT", 587)
    MAIL_USE_TLS = _env_flag("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "").strip()
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "").strip()
    MAIL_TIMEOUT_SECONDS = _env_int("MAIL_TIMEOUT_SECONDS", 10)
    MAIL_SUPPRESS_SEND = _env_flag("MAIL_SUPPRESS_SEND", False)

    EMAIL_VERIFICATION_TTL_MINUTES = _env_int("EMAIL_VERIFICATION_TTL_MINUTES", 10)
    EMAIL_VERIFICATION_MAX_ATTEMPTS = _env_int("EMAIL_VERIFICATION_MAX_ATTEMPTS", 5)
    EMAIL_VERIFICATION_RESEND_SECONDS = _env_int("EMAIL_VERIFICATION_RESEND_SECONDS", 60)
    PASSWORD_RESET_TTL_MINUTES = _env_int("PASSWORD_RESET_TTL_MINUTES", 60)

    # Acceso privilegiado de plataforma.
    PLATFORM_ADMIN_KEY = os.environ.get("PLATFORM_ADMIN_KEY", "").strip()
    PLATFORM_ADMIN_TOTP_SECRET = os.environ.get("PLATFORM_ADMIN_TOTP_SECRET", "").strip()
    PLATFORM_MFA_REQUIRED = _env_flag("PLATFORM_MFA_REQUIRED", False)
    PLATFORM_SESSION_IDLE_MINUTES = _env_int("PLATFORM_SESSION_IDLE_MINUTES", 15)
    PLATFORM_SESSION_ABSOLUTE_MINUTES = _env_int("PLATFORM_SESSION_ABSOLUTE_MINUTES", 120)
    PLATFORM_MFA_PENDING_MINUTES = _env_int("PLATFORM_MFA_PENDING_MINUTES", 5)
    JWT_EXPIRES_MINUTES = _env_int("JWT_EXPIRES_MINUTES", 480)

    # Logging estructurado
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    LOG_JSON = _env_flag("LOG_JSON", False)
    SENTRY_DSN = os.environ.get("SENTRY_DSN", "").strip()
    SENTRY_TRACES_SAMPLE_RATE = _env_float("SENTRY_TRACES_SAMPLE_RATE", 0.1)
    METRICS_TOKEN = os.environ.get("METRICS_TOKEN", "").strip()
    OPS_ALERT_COOLDOWN_SECONDS = _env_int("OPS_ALERT_COOLDOWN_SECONDS", 300)
    OPS_ALERT_EMAIL = os.environ.get("OPS_ALERT_EMAIL", "").strip()
    DB_HEALTH_DEGRADED_MS = _env_int("DB_HEALTH_DEGRADED_MS", 750)

    # Redis/Render Key Value: límites compartidos, locks y heartbeat de workers.
    REDIS_URL = os.environ.get("REDIS_URL", "").strip()
    RATELIMIT_STORAGE_URI = REDIS_URL or "memory://"
    RATELIMIT_HEADERS_ENABLED = True
    DISTRIBUTED_RATE_LIMITS_REQUIRED = _env_flag("DISTRIBUTED_RATE_LIMITS_REQUIRED", False)
    REDIS_HEALTH_DEGRADED_MS = _env_int("REDIS_HEALTH_DEGRADED_MS", 250)
    WORKER_HEARTBEAT_REQUIRED = _env_flag("WORKER_HEARTBEAT_REQUIRED", False)
    WORKER_HEARTBEAT_MAX_AGE_SECONDS = _env_int("WORKER_HEARTBEAT_MAX_AGE_SECONDS", 90)
    WORKER_POLL_SECONDS = _env_float("WORKER_POLL_SECONDS", 2.0)
    WORKER_WEBHOOK_BATCH_SIZE = _env_int("WORKER_WEBHOOK_BATCH_SIZE", 50)
    WORKER_MAINTENANCE_ENABLED = _env_flag("WORKER_MAINTENANCE_ENABLED", False)
    WORKER_MAINTENANCE_INTERVAL_SECONDS = _env_int(
        "WORKER_MAINTENANCE_INTERVAL_SECONDS", 3600
    )

    # Arranque: tareas pesadas desactivadas por defecto en producción
    RUN_STARTUP_TASKS = _env_flag("RUN_STARTUP_TASKS", False)
    # Migraciones legacy ensure_* (transición a Flask-Migrate)
    RUN_LEGACY_SCHEMA_MIGRATIONS = _env_flag("RUN_LEGACY_SCHEMA_MIGRATIONS", False)

    # Suite documental: hybrid | open | locked (ver app/docs_access.py · docs/ACCESS.md)
    DOCS_ACCESS_POLICY = (
        os.environ.get("DOCS_ACCESS_POLICY", "hybrid").strip().lower() or "hybrid"
    )

    # Neon / PostgreSQL
    NEON_PROJECT_ID = os.environ.get("NEON_PROJECT_ID", "").strip()
    NEON_API_KEY = os.environ.get("NEON_API_KEY", "").strip()
    BACKUP_DIR = os.environ.get("BACKUP_DIR", str(BASE_DIR / "backups"))

    # Archivos de clientes. ``s3`` funciona con S3, Cloudflare R2 y Backblaze B2.
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local").strip().lower()
    STORAGE_LOCAL_ROOT = os.environ.get(
        "STORAGE_LOCAL_ROOT", str(BASE_DIR / "data" / "object_storage")
    )
    STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET", "").strip()
    STORAGE_ENDPOINT_URL = os.environ.get("STORAGE_ENDPOINT_URL", "").strip()
    STORAGE_REGION = os.environ.get("STORAGE_REGION", "auto").strip()
    STORAGE_ACCESS_KEY_ID = os.environ.get("STORAGE_ACCESS_KEY_ID", "").strip()
    STORAGE_SECRET_ACCESS_KEY = os.environ.get("STORAGE_SECRET_ACCESS_KEY", "")
    # Evita errores cuando Neon suspende la BD por inactividad (scale-to-zero)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get("SECRET_KEY", "").strip() or "dev-mantenimiento-pro"
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("DATABASE_URL", _default_sqlite_uri())
    )
    SQLALCHEMY_ENGINE_OPTIONS = engine_options_for(
        os.environ.get("DATABASE_URL", _default_sqlite_uri())
    )
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG").upper()
    LOG_JSON = False
    RUN_STARTUP_TASKS = _env_flag("RUN_STARTUP_TASKS", True)


class ProductionConfig(Config):
    DEBUG = False
    PLATFORM_MFA_REQUIRED = _env_flag("PLATFORM_MFA_REQUIRED", True)
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    LOG_JSON = True
    DISTRIBUTED_RATE_LIMITS_REQUIRED = True
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("DATABASE_URL", _default_sqlite_uri())
    )

    @staticmethod
    def init_app(app) -> None:
        from app.security_hardening import enforce_production_configuration

        enforce_production_configuration(app)


class WorkerConfig(Config):
    """Proceso sin HTTP: PostgreSQL, Redis, webhooks y tareas periódicas."""

    DEBUG = False
    LOG_JSON = True
    DISTRIBUTED_RATE_LIMITS_REQUIRED = True
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("DATABASE_URL", _default_sqlite_uri())
    )

    @staticmethod
    def init_app(app) -> None:
        from app.security_hardening import enforce_worker_configuration

        enforce_worker_configuration(app)


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    RUN_STARTUP_TASKS = False
    RUN_LEGACY_SCHEMA_MIGRATIONS = False
    MAIL_SUPPRESS_SEND = True
    # Tests unitarios no simulan login de docs salvo test_docs_access
    DOCS_ACCESS_POLICY = os.environ.get("DOCS_ACCESS_POLICY", "open").strip().lower() or "open"

    @staticmethod
    def init_app(app) -> None:
        """Permite ejecutar la misma suite contra PostgreSQL sin afectar el local."""
        test_database_url = os.environ.get("TEST_DATABASE_URL", "").strip()
        if not test_database_url:
            return
        app.config["SQLALCHEMY_DATABASE_URI"] = normalize_database_url(test_database_url)
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_options_for(test_database_url)


config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "worker": WorkerConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def resolve_config_name() -> str:
    explicit = os.environ.get("FLASK_CONFIG", "").strip().lower()
    if explicit in config_by_name:
        return explicit
    env = (os.environ.get("FLASK_ENV") or os.environ.get("ENV") or "development").strip().lower()
    if env == "production":
        return "production"
    if env == "testing":
        return "testing"
    return "development"
