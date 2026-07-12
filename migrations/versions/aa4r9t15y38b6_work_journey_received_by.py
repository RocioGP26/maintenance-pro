"""Agrega recibido por a cada jornada de una OT.

Revision ID: aa4r9t15y38b6
Revises: z3q8s04x27a5
"""
from alembic import op
import sqlalchemy as sa


revision = "aa4r9t15y38b6"
down_revision = "z3q8s04x27a5"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("work_order_jornadas")}
    if "recibido_por" not in columns:
        with op.batch_alter_table("work_order_jornadas") as batch_op:
            batch_op.add_column(sa.Column("recibido_por", sa.String(200), nullable=True))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("work_order_jornadas")}
    if "recibido_por" in columns:
        with op.batch_alter_table("work_order_jornadas") as batch_op:
            batch_op.drop_column("recibido_por")
