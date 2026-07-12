"""Separa vendedor del rol técnico.

Revision ID: r5h8j26p39s7
Revises: q4g7i15o28r6
"""
from alembic import op


revision = "r5h8j26p39s7"
down_revision = "q4g7i15o28r6"
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
