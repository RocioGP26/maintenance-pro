"""Convierte a correctivas las OT de tickets aún no ejecutadas.

Revision ID: ab5s0u26z49c7
Revises: aa4r9t15y38b6
"""
from alembic import op


revision = "ab5s0u26z49c7"
down_revision = "aa4r9t15y38b6"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE work_orders
        SET tipo = 'correctivo'
        WHERE tipo = 'emergencia'
          AND id IN (
              SELECT i.work_order_id
              FROM incidents i
              WHERE i.work_order_id IS NOT NULL
          )
          AND NOT EXISTS (
              SELECT 1 FROM work_order_jornadas j
              WHERE j.work_order_id = work_orders.id
          )
        """
    )


def downgrade():
    pass
