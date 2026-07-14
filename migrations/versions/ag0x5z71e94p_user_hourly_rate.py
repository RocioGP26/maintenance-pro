"""Agrega tarifa hora de usuario y snapshot por jornada.

Revision ID: ag0x5z71e94p
Revises: af9w4y60d83n
"""

from alembic import op
import sqlalchemy as sa


revision = "ag0x5z71e94p"
down_revision = "af9w4y60d83n"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("tarifa_hora", sa.Numeric(precision=14, scale=2), nullable=False, server_default="0")
        )
    with op.batch_alter_table("work_order_jornadas") as batch_op:
        batch_op.add_column(
            sa.Column("tarifa_hora_aplicada", sa.Numeric(precision=14, scale=2), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("work_order_jornadas") as batch_op:
        batch_op.drop_column("tarifa_hora_aplicada")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("tarifa_hora")
