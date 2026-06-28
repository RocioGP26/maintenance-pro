"""Copia de seguridad lógica de la base de datos (Neon/PostgreSQL o SQLite)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def _backup_dir() -> Path:
    path = Path(os.environ.get("BACKUP_DIR", "backups"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def backup_sqlite(database_url: str) -> Path:
    """Copia el archivo SQLite referenciado en la URI."""
    raw = database_url.replace("sqlite:///", "", 1)
    src = Path(raw)
    if not src.is_file():
        raise FileNotFoundError(f"No se encontró la base SQLite: {src}")
    dest = _backup_dir() / f"sqlite_{_timestamp()}.db"
    shutil.copy2(src, dest)
    logger.info("Backup SQLite creado", extra={"path": str(dest)})
    return dest


def backup_postgresql(database_url: str) -> Path:
    """Ejecuta pg_dump contra la URI de PostgreSQL (compatible con Neon)."""
    parsed = urlparse(database_url.replace("postgresql+psycopg://", "postgresql://", 1))
    dest = _backup_dir() / f"neon_{_timestamp()}.sql.gz"

    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password

    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    user = parsed.username or "postgres"
    dbname = (parsed.path or "/postgres").lstrip("/") or "postgres"

    cmd = [
        "pg_dump",
        "-h",
        host,
        "-p",
        port,
        "-U",
        user,
        "-d",
        dbname,
        "--no-owner",
        "--no-acl",
        "-F",
        "p",
    ]
    if "sslmode=require" in (parsed.query or ""):
        cmd.extend(["--sslmode", "require"])

    logger.info("Iniciando pg_dump", extra={"host": host, "database": dbname})

    with open(dest, "wb") as out:
        proc = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            dest.unlink(missing_ok=True)
            raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))

    logger.info("Backup PostgreSQL creado", extra={"path": str(dest)})
    return dest


def run_backup(database_url: str) -> Path:
    """Detecta el dialecto y ejecuta el backup apropiado."""
    url = (database_url or "").strip()
    if not url:
        raise ValueError("DATABASE_URL no configurada")

    if url.startswith("sqlite"):
        return backup_sqlite(url)
    if "postgresql" in url or "postgres" in url:
        return backup_postgresql(url)

    raise ValueError(f"Dialecto no soportado para backup: {url.split('://')[0]}")


def prune_old_backups(retention_days: int = 7) -> int:
    """Elimina backups más antiguos que retention_days."""
    cutoff = datetime.now(timezone.utc).timestamp() - (retention_days * 86400)
    removed = 0
    for f in _backup_dir().glob("*"):
        if f.is_file() and f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    if removed:
        logger.info("Backups antiguos eliminados", extra={"count": removed})
    return removed
