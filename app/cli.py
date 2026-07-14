"""Comandos CLI de Flask (migraciones, mantenimiento, backups)."""

from __future__ import annotations

import os

import click
from flask import current_app
from flask.cli import with_appcontext

from app.startup import run_legacy_schema_migrations, run_maintenance_tasks
from app.version import __version__, get_build_commit


@click.group()
def maintenance():
    """Tareas de mantenimiento periódicas (cron, Render cron, GitHub Actions)."""
    pass


@maintenance.command("run")
@with_appcontext
def maintenance_run():
    """Sincroniza OT, suscripciones y vencimientos."""
    stats = run_maintenance_tasks()
    click.echo(f"Mantenimiento completado: {stats}")


@maintenance.command("legacy-migrate")
@with_appcontext
def maintenance_legacy_migrate():
    """Ejecuta migraciones ensure_* legacy (transición a Flask-Migrate)."""
    run_legacy_schema_migrations()
    click.echo("Migraciones legacy completadas.")


@click.command("backup-db")
@with_appcontext
def backup_db():
    """Copia de seguridad lógica de la base de datos (pg_dump o SQLite)."""
    from app.backup_service import prune_old_backups, run_backup

    path = run_backup(current_app.config.get("SQLALCHEMY_DATABASE_URI", ""))
    retention = int(os.environ.get("BACKUP_RETENTION_DAYS", "7"))
    prune_old_backups(retention)
    click.echo(f"Backup guardado en: {path}")


@click.command("version")
def version_command():
    """Muestra la versión SemVer y el build Git de Maintix."""
    click.echo(f"Maintix v{__version__}")
    click.echo(f"Build: {get_build_commit() or 'local'}")


def register_cli(app) -> None:
    app.cli.add_command(maintenance)
    app.cli.add_command(backup_db)
    app.cli.add_command(version_command)
