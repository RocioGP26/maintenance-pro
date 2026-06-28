"""Inicialización de la aplicación: tareas ligeras vs pesadas."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def run_lightweight_startup() -> None:
    """Tareas idempotentes y rápidas necesarias en cada despliegue."""
    from sqlalchemy import inspect

    from app import db
    from app.platform_config_service import ensure_platform_config

    tables = set(inspect(db.engine).get_table_names())
    if "reglas_plataforma" not in tables:
        logger.debug("Esquema incompleto; omitiendo startup ligero (pendiente flask db upgrade)")
        return

    ensure_platform_config()
    logger.debug("Startup ligero completado")


def run_legacy_schema_migrations() -> None:
    """Migraciones ad hoc ensure_* — solo durante transición a Flask-Migrate."""
    from app import models

    logger.info("Ejecutando migraciones legacy ensure_*")
    models.ensure_saas_schema()
    models.ensure_machine_tipo_equipo_column()
    models.ensure_machine_types_sector_column()
    models.ensure_machines_machine_type_fk()


def run_dev_seeds() -> None:
    """Datos de demostración y usuario admin (solo desarrollo)."""
    from app import models

    models.seed_machine_types_if_empty()
    models.seed_if_empty()


def run_maintenance_tasks(empresa_id: int | None = None) -> dict:
    """
    Tareas periódicas: sincronización de OT y ciclo de suscripciones.
    Ejecutar vía cron o `flask maintenance run`, no en cada arranque.
    """
    from app.subscription_service import (
        backfill_estado_ciclo_suscripciones,
        verificar_vencimientos,
    )
    from app.work_order_status import sincronizar_estados_ordenes

    sincronizar_estados_ordenes(empresa_id)
    stats: dict = {
        "suscripciones_backfill": backfill_estado_ciclo_suscripciones(),
    }
    stats.update(verificar_vencimientos())
    logger.info("Tareas de mantenimiento completadas: %s", stats)
    return stats


def run_startup(app) -> None:
    """Orquesta el arranque según la configuración del entorno."""
    with app.app_context():
        run_lightweight_startup()

        if app.config.get("RUN_LEGACY_SCHEMA_MIGRATIONS"):
            run_legacy_schema_migrations()

        if app.config.get("RUN_STARTUP_TASKS"):
            run_dev_seeds()
