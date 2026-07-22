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


@click.command("verify-backup")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=str))
def verify_backup_command(path: str):
    """Verifica integridad y formato de una copia sin restaurarla."""
    from app.backup_service import verify_backup

    verify_backup(path)
    click.echo(f"Backup verificado: {path}")


@click.command("restore-db")
@click.argument("path", type=click.Path(exists=True, dir_okay=False, path_type=str))
@click.option("--target", required=True, help="Archivo SQLite o URL PostgreSQL de destino.")
@click.option("--yes", is_flag=True, help="Confirma que el destino puede ser reemplazado.")
def restore_db_command(path: str, target: str, yes: bool):
    """Restaura una copia en un destino indicado expresamente."""
    if not yes:
        raise click.ClickException("Usa --yes después de verificar el destino de restauración.")
    from app.backup_service import restore_postgresql_backup, restore_sqlite_backup

    if path.endswith(".db"):
        restored = restore_sqlite_backup(path, target)
        click.echo(f"SQLite restaurado y verificado en: {restored}")
    elif path.endswith(".sql.gz"):
        restore_postgresql_backup(path, target)
        click.echo("PostgreSQL restaurado correctamente.")
    else:
        raise click.ClickException("Formato de respaldo no reconocido.")


@click.command("migrate-storage")
@click.option("--apply", is_flag=True, help="Copia los archivos y actualiza sus referencias.")
@with_appcontext
def migrate_storage_command(apply: bool):
    """Inventaría o migra archivos históricos al backend configurado."""
    from app.storage_migration import migrate_legacy_storage

    stats = migrate_legacy_storage(apply=apply)
    mode = "APLICADA" if apply else "SIMULACIÓN"
    click.echo(f"Migración de almacenamiento ({mode}): {stats}")
    if not apply:
        click.echo("Ejecuta nuevamente con --apply después de revisar el inventario.")


@click.command("version")
def version_command():
    """Muestra la versión SemVer y el build Git de Roustix."""
    click.echo(f"Roustix v{__version__}")
    click.echo(f"Build: {get_build_commit() or 'local'}")


def register_cli(app) -> None:
    app.cli.add_command(maintenance)
    app.cli.add_command(backup_db)
    app.cli.add_command(verify_backup_command)
    app.cli.add_command(restore_db_command)
    app.cli.add_command(migrate_storage_command)
    app.cli.add_command(version_command)
