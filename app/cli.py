"""Comandos CLI de Flask (migraciones, mantenimiento, backups)."""

from __future__ import annotations

import json
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


@click.command("backup-storage")
@click.option(
    "--manifest",
    default="storage.manifest.json",
    show_default=True,
    type=click.Path(dir_okay=False, path_type=str),
)
def backup_storage_command(manifest: str):
    """Replica S3 al bucket de recuperación y genera su manifiesto."""
    from app.storage_backup import backup_s3_storage

    stats = backup_s3_storage(manifest)
    click.echo(
        "Backup S3 completado: "
        f"{stats['copied']} copiados, {stats['skipped']} sin cambios, "
        f"{stats['object_count']} totales."
    )


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
@click.option("--inventory-only", is_flag=True, help="Solo cuenta referencias legacy en BD.")
@click.option("--list", "list_pending", is_flag=True, help="Lista refs legacy con local/remote.")
@click.option(
    "--clear-broken",
    is_flag=True,
    help="Limpia refs legacy sin archivo local ni objeto en R2 (usar con --apply).",
)
@with_appcontext
def migrate_storage_command(apply: bool, inventory_only: bool, list_pending: bool, clear_broken: bool):
    """Inventaría o migra archivos históricos al backend configurado."""
    from app.storage_migration import (
        clear_broken_legacy_refs,
        inventory_legacy_refs,
        list_legacy_pending,
        migrate_legacy_storage,
    )

    modes = sum(bool(x) for x in (inventory_only, list_pending, clear_broken))
    if modes > 1:
        raise click.ClickException("Usa solo uno de: --inventory-only, --list, --clear-broken.")
    if inventory_only and apply:
        raise click.ClickException("Usa --inventory-only o --apply, no ambos.")

    if inventory_only:
        inv = inventory_legacy_refs()
        click.echo(f"Inventario de referencias: {inv}")
        if inv.get("legacy_total", 0) == 0:
            click.echo("OK: no quedan referencias legacy pendientes en BD.")
        else:
            click.echo(
                f"Pendientes: {inv['legacy_total']} refs. "
                "Ejecuta `migrate-storage --list` y luego simulación / `--apply`."
            )
        return

    if list_pending:
        rows = list_legacy_pending()
        if not rows:
            click.echo("OK: no hay referencias legacy pendientes.")
            return
        for row in rows:
            flags = []
            flags.append("local" if row["local"] else "no-local")
            flags.append("remote" if row["remote"] else "no-remote")
            click.echo(
                f"{row['kind']}#{row['id']}  {row['legacy']}  ->  {row['key'] or '-'}  [{', '.join(flags)}]"
            )
        click.echo(f"Total: {len(rows)}. Si remote=sí, `--apply` reescribe la BD sin disco local.")
        return

    if clear_broken:
        result = clear_broken_legacy_refs(apply=apply)
        mode = "APLICADA" if apply else "SIMULACIÓN"
        click.echo(f"Limpieza de refs rotas ({mode}): {result}")
        if not apply:
            click.echo("Ejecuta con `--clear-broken --apply` para vaciar esas refs en BD.")
        return

    stats = migrate_legacy_storage(apply=apply)
    mode = "APLICADA" if apply else "SIMULACIÓN"
    inv = stats.pop("inventory", {})
    click.echo(f"Migración de almacenamiento ({mode}): {stats}")
    click.echo(f"Inventario post-paso: {inv}")
    if not apply:
        click.echo("Ejecuta nuevamente con --apply después de revisar. missing>0 -> --list.")
    elif inv.get("legacy_total", 0) == 0:
        click.echo(
            "Cutover BD completo. Conserva static/uploads hasta validar medios; "
            "luego bórralos (metering S3 ya no suma legacy)."
        )
    elif stats.get("missing", 0):
        click.echo(
            "Quedan refs sin archivo local ni objeto remoto. "
            "Revisa con `--list` o límpialas con `--clear-broken --apply`."
        )


@click.command("version")
def version_command():
    """Muestra la versión SemVer y el build Git de Roustix."""
    click.echo(f"Roustix v{__version__}")
    click.echo(f"Build: {get_build_commit() or 'local'}")


@click.group()
def webhooks():
    """Worker y utilidades de webhooks (Sprint 22.3)."""
    pass


@webhooks.command("deliver")
@click.option("--limit", default=50, show_default=True, help="Máximo de entregas a procesar.")
@with_appcontext
def webhooks_deliver(limit: int):
    """Procesa entregas pendientes con firma HMAC y reintentos."""
    from app.integrations.webhooks import process_pending_deliveries

    stats = process_pending_deliveries(limit=limit)
    click.echo(f"Webhooks: {stats}")


@webhooks.command("prune")
@click.option("--empresa-id", type=int, default=None, help="Limita la retención a un tenant.")
@with_appcontext
def webhooks_prune(empresa_id: int | None):
    """Purga historial de entregas según retención del plan."""
    from app.integrations.webhooks import prune_deliveries
    from app import db

    removed = prune_deliveries(empresa_id)
    db.session.commit()
    click.echo(f"Entregas eliminadas: {removed}")


@click.group("email-outbox")
def email_outbox():
    """Utilidades controladas para certificar la outbox de correo."""
    pass


@email_outbox.command("certify-idempotency")
@click.option("--empresa-slug", required=True, help="Slug exacto del tenant piloto.")
@click.option("--user-email", required=True, help="Correo del usuario receptor del tenant.")
@click.option(
    "--run-id", required=True,
    help="Identificador estable del ensayo; reutilízalo para consultar el mismo sobre.",
)
@with_appcontext
def certify_email_outbox_idempotency(
    empresa_slug: str, user_email: str, run_id: str,
) -> None:
    """Encola dos veces una prueba y demuestra que sólo se crea un sobre."""
    from app import db
    from app.email_service import send_templated_email
    from app.email_verification_service import normalize_email
    from app.models import EmailOutbox, Empresa, User

    safe_run_id = (run_id or "").strip()
    if not safe_run_id or len(safe_run_id) > 80:
        raise click.ClickException("run-id debe contener entre 1 y 80 caracteres.")
    empresa = Empresa.query.filter_by(slug=(empresa_slug or "").strip()).first()
    if empresa is None:
        raise click.ClickException("No existe el tenant indicado.")
    user = User.query.filter_by(
        empresa_id=empresa.id, email=normalize_email(user_email), activo=True,
    ).first()
    if user is None:
        raise click.ClickException("No existe un usuario activo con ese correo en el tenant.")

    key = f"certification:{safe_run_id}"
    arguments = {
        "empresa_id": empresa.id,
        "recipient": normalize_email(user.email),
        "subject": "Certificación operativa de correo Roustix",
        "template_name": "outbox_certification",
        "context": {"user": user, "empresa": empresa, "run_id": safe_run_id},
        "idempotency_key": key,
    }
    first = send_templated_email(**arguments)
    first_id = first.id
    second = send_templated_email(**arguments)
    second_id = second.id
    db.session.commit()

    count = EmailOutbox.query.filter_by(
        empresa_id=empresa.id, idempotency_key=key,
    ).count()
    item = db.session.get(EmailOutbox, first_id)
    approved = first_id == second_id and count == 1
    result = {
        "approved": approved,
        "same_id": first_id == second_id,
        "row_count": count,
        "status": item.status if item is not None else "missing",
        "attempts": int(item.attempts or 0) if item is not None else 0,
        "sent": bool(item and item.sent_at),
    }
    click.echo(json.dumps(result, sort_keys=True))
    if not approved:
        raise click.ClickException("La outbox no superó el control de idempotencia.")


def register_cli(app) -> None:
    app.cli.add_command(maintenance)
    app.cli.add_command(backup_db)
    app.cli.add_command(backup_storage_command)
    app.cli.add_command(verify_backup_command)
    app.cli.add_command(restore_db_command)
    app.cli.add_command(migrate_storage_command)
    app.cli.add_command(version_command)
    app.cli.add_command(webhooks)
    app.cli.add_command(email_outbox)
