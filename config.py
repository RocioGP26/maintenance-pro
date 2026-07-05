"""Configuración por entorno (desarrollo, producción, pruebas)."""

from __future__ import annotations

import os
from pathlib import Path

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


class Config:
    """Valores compartidos entre entornos."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "").strip()
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging estructurado
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
    LOG_JSON = _env_flag("LOG_JSON", False)

    # Arranque: tareas pesadas desactivadas por defecto en producción
    RUN_STARTUP_TASKS = _env_flag("RUN_STARTUP_TASKS", False)
    # Migraciones legacy ensure_* (transición a Flask-Migrate)
    RUN_LEGACY_SCHEMA_MIGRATIONS = _env_flag("RUN_LEGACY_SCHEMA_MIGRATIONS", False)

    # Neon / PostgreSQL
    NEON_PROJECT_ID = os.environ.get("NEON_PROJECT_ID", "").strip()
    NEON_API_KEY = os.environ.get("NEON_API_KEY", "").strip()
    BACKUP_DIR = os.environ.get("BACKUP_DIR", str(BASE_DIR / "backups"))
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
    SESSION_COOKIE_SECURE = True
    LOG_JSON = True
    SQLALCHEMY_DATABASE_URI = normalize_database_url(
        os.environ.get("DATABASE_URL", _default_sqlite_uri())
    )

    @staticmethod
    def init_app(app) -> None:
        if not app.config.get("SECRET_KEY"):
            raise RuntimeError(
                "SECRET_KEY debe estar definida en producción (FLASK_ENV=production)."
            )
        if not os.environ.get("DATABASE_URL", "").strip():
            import logging

            logging.getLogger(__name__).warning(
                "DATABASE_URL no está configurada: se usa SQLite local. "
                "En producción conecta Neon/PostgreSQL para persistencia."
            )


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    RUN_STARTUP_TASKS = False
    RUN_LEGACY_SCHEMA_MIGRATIONS = False


config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
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
