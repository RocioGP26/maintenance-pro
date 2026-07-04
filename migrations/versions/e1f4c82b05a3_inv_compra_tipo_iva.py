"""inv_compra tipo iva y totales

Revision ID: e1f4c82b05a3
Revises: d9e3b71a04f2
Create Date: 2026-07-04 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "e1f4c82b05a3"
down_revision = "d9e3b71a04f2"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("inv_compras")}
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        if "tipo_iva" not in cols:
            batch_op.add_column(
                sa.Column("tipo_iva", sa.String(length=16), nullable=True, server_default="exento")
            )
        if "subtotal" not in cols:
            batch_op.add_column(sa.Column("subtotal", sa.Float(), nullable=True, server_default="0"))
        if "monto_iva" not in cols:
            batch_op.add_column(sa.Column("monto_iva", sa.Float(), nullable=True, server_default="0"))


def downgrade():
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        batch_op.drop_column("monto_iva")
        batch_op.drop_column("subtotal")
        batch_op.drop_column("tipo_iva")
