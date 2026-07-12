"""Separa vendedor del rol técnico.

Revision ID: m0c3e71k84j2
Revises: l9b2d60j73i1
"""
from alembic import op


revision = "m0c3e71k84j2"
down_revision = "l9b2d60j73i1"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE users
        SET rol = 'vendedor'
        WHERE rol = 'tecnico'
          AND empresa_id IN (
            SELECT id FROM empresas
            WHERE lower(coalesce(modulos_activos_json, '')) LIKE '%inventario%'
              AND lower(coalesce(modulos_activos_json, '')) NOT LIKE '%mantenimiento%'
          )
        """
    )


def downgrade():
    op.execute("UPDATE users SET rol = 'tecnico' WHERE rol = 'vendedor'")
