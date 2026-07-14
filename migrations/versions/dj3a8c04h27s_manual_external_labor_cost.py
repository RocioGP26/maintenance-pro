"""Agrega costo MDO manual para jornadas externas.

Revision ID: dj3a8c04h27s
Revises: ci2z7b93g16r
"""

from alembic import op
import sqlalchemy as sa


revision = "dj3a8c04h27s"
down_revision = "ci2z7b93g16r"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("work_order_jornadas") as batch_op:
        batch_op.add_column(
            sa.Column("costo_mano_obra_manual", sa.Numeric(precision=14, scale=2), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("work_order_jornadas") as batch_op:
        batch_op.drop_column("costo_mano_obra_manual")
