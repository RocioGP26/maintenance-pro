"""Migraciones en despliegue: baseline Alembic para BDs legacy + upgrade pendiente."""

from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import inspect

from flask_migrate import stamp, upgrade

from app import create_app, db

INITIAL_REVISION = "a6dc612735e8"
app = create_app()


def main() -> int:
    with app.app_context():
        tables = set(inspect(db.engine).get_table_names())

        if not tables or "empresas" not in tables:
            print("BD nueva o vacía: aplicando todas las migraciones.")
            upgrade()
            return 0

        if "alembic_version" not in tables:
            print(
                "BD existente sin alembic_version: marcando revisión inicial "
                f"{INITIAL_REVISION}."
            )
            stamp(revision=INITIAL_REVISION)

        print("Aplicando migraciones pendientes...")
        upgrade()
        print("Migraciones completadas.")
        return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error en migraciones: {exc}", file=sys.stderr)
        raise
