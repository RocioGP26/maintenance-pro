"""Crea datos mínimos y deterministas para el smoke E2E de CI."""

from __future__ import annotations

import os
from datetime import UTC, datetime

from app import create_app, db
from app.models import Empresa, User, UserRole


def seed() -> tuple[int, int]:
    database_url = os.environ.get("TEST_DATABASE_URL", "").strip()
    if not database_url.startswith(("postgresql://", "postgresql+psycopg://")):
        raise RuntimeError("ci_seed_e2e solo puede ejecutarse con TEST_DATABASE_URL PostgreSQL.")

    password = os.environ.get("E2E_USER_PASSWORD", "")
    if len(password) < 12:
        raise RuntimeError("E2E_USER_PASSWORD debe contener al menos 12 caracteres.")

    app = create_app("testing")
    with app.app_context():
        empresa = Empresa.query.filter_by(slug="ci-e2e").first()
        if empresa is None:
            empresa = Empresa(
                razon_social="Roustix CI E2E",
                nit="CI-0001",
                slug="ci-e2e",
                email="ci-e2e@example.invalid",
                email_verified_at=datetime.now(UTC).replace(tzinfo=None),
                modulos_activos_json='["mantenimiento"]',
            )
            db.session.add(empresa)
            db.session.flush()
        else:
            empresa.email_verified_at = empresa.email_verified_at or datetime.now(UTC).replace(tzinfo=None)
            empresa.suspendida = False

        user = User.query.filter_by(empresa_id=empresa.id, username="ci_admin").first()
        if user is None:
            user = User(
                empresa_id=empresa.id,
                username="ci_admin",
                email="ci-admin@example.invalid",
                nombre_visible="Administrador CI",
                rol=UserRole.ADMIN.value,
                activo=True,
                onboarding_completado=True,
            )
            db.session.add(user)
        user.activo = True
        user.bloqueado = False
        user.onboarding_completado = True
        user.set_password(password)
        db.session.commit()
        return empresa.id, user.id


if __name__ == "__main__":
    company_id, user_id = seed()
    print(f"Semilla E2E lista: empresa={company_id}, usuario={user_id}")
