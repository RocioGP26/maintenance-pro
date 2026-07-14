"""Agrega costo de herramientas por jornada de OT.

Revision ID: ci2z7b93g16r
Revises: bh1y6a82f05q
"""

from alembic import op
import sqlalchemy as sa


revision = "ci2z7b93g16r"
down_revision = "bh1y6a82f05q"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("work_order_jornadas") as batch_op:
        batch_op.add_column(
            sa.Column(
                "costo_herramientas",
                sa.Numeric(precision=14, scale=2),
                nullable=False,
                server_default="0",
            )
        )


def downgrade():
    with op.batch_alter_table("work_order_jornadas") as batch_op:
        batch_op.drop_column("costo_herramientas")
