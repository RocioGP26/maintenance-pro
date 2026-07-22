"""Copia de seguridad lógica de la base de datos (Neon/PostgreSQL o SQLite)."""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import gzip
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

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
    verify_sqlite_backup(dest)
    logger.info("Backup SQLite creado", extra={"path": str(dest)})
    return dest


def backup_postgresql(database_url: str) -> Path:
    """Ejecuta pg_dump contra la URI de PostgreSQL (compatible con Neon)."""
    parsed = urlparse(database_url.replace("postgresql+psycopg://", "postgresql://", 1))
    dest = _backup_dir() / f"neon_{_timestamp()}.sql.gz"

    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = unquote(parsed.password)
    sslmode = parse_qs(parsed.query).get("sslmode", [""])[0]
    if sslmode:
        env["PGSSLMODE"] = sslmode

    host = parsed.hostname or "localhost"
    port = str(parsed.port or 5432)
    user = unquote(parsed.username) if parsed.username else "postgres"
    dbname = unquote((parsed.path or "/postgres").lstrip("/")) or "postgres"

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
    logger.info("Iniciando pg_dump", extra={"host": host, "database": dbname})

    with gzip.open(dest, "wb") as out:
        proc = subprocess.run(cmd, env=env, stdout=out, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            dest.unlink(missing_ok=True)
            raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))

    verify_postgresql_backup(dest)
    logger.info("Backup PostgreSQL creado y verificado", extra={"path": str(dest)})
    return dest


def verify_sqlite_backup(path: Path) -> None:
    """Comprueba que SQLite puede abrir la copia y que su estructura es íntegra."""
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("El respaldo SQLite está vacío o no existe.")
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        result = connection.execute("PRAGMA integrity_check").fetchone()
    finally:
        connection.close()
    if not result or result[0] != "ok":
        raise ValueError(f"El respaldo SQLite no superó integrity_check: {result}")


def verify_postgresql_backup(path: Path) -> None:
    """Valida compresión, contenido y finalización de un dump SQL de PostgreSQL."""
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("El respaldo PostgreSQL está vacío o no existe.")
    with gzip.open(path, "rb") as source:
        beginning = source.read(4096)
        while source.read(1024 * 1024):
            pass
    if b"PostgreSQL database dump" not in beginning:
        raise ValueError("El archivo no parece ser un dump SQL válido de PostgreSQL.")


def verify_backup(path: str | Path) -> None:
    source = Path(path)
    if source.suffix == ".db":
        verify_sqlite_backup(source)
    elif source.name.endswith(".sql.gz"):
        verify_postgresql_backup(source)
    else:
        raise ValueError("Formato de respaldo no reconocido (.db o .sql.gz).")


def restore_sqlite_backup(path: str | Path, target: str | Path) -> Path:
    """Restaura SQLite en un archivo destino nuevo o reemplazable."""
    source = Path(path)
    destination = Path(target)
    verify_sqlite_backup(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".restore-tmp")
    shutil.copy2(source, temporary)
    verify_sqlite_backup(temporary)
    os.replace(temporary, destination)
    return destination


def restore_postgresql_backup(path: str | Path, target_url: str) -> None:
    """Restaura un dump SQL en una base PostgreSQL indicada expresamente."""
    source = Path(path)
    verify_postgresql_backup(source)
    parsed = urlparse(target_url.replace("postgresql+psycopg://", "postgresql://", 1))
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ValueError("La URL destino debe ser PostgreSQL.")
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = unquote(parsed.password)
    sslmode = parse_qs(parsed.query).get("sslmode", [""])[0]
    if sslmode:
        env["PGSSLMODE"] = sslmode
    cmd = [
        "psql", "-v", "ON_ERROR_STOP=1", "-h", parsed.hostname or "localhost",
        "-p", str(parsed.port or 5432), "-U", unquote(parsed.username) if parsed.username else "postgres",
        "-d", unquote((parsed.path or "/postgres").lstrip("/")) or "postgres",
    ]
    with gzip.open(source, "rb") as dump:
        proc = subprocess.run(cmd, env=env, stdin=dump, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode("utf-8", errors="replace"))


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
