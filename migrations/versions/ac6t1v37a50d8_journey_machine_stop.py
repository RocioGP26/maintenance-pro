"""Registra el paro del activo por cada jornada de OT.

Revision ID: ac6t1v37a50d8
Revises: ab5s0u26z49c7
"""
from alembic import op
import sqlalchemy as sa


revision = "ac6t1v37a50d8"
down_revision = "ab5s0u26z49c7"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("work_order_jornadas")}
    if "requirio_paro" not in columns:
        with op.batch_alter_table("work_order_jornadas") as batch_op:
            batch_op.add_column(sa.Column("requirio_paro", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("work_order_jornadas")}
    if "requirio_paro" in columns:
        with op.batch_alter_table("work_order_jornadas") as batch_op:
            batch_op.drop_column("requirio_paro")
