"""inv_compra fecha factura proveedor

Revision ID: g4c7e15e28d6
Revises: f2a5d93c06b4
Create Date: 2026-07-04 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "g4c7e15e28d6"
down_revision = "f2a5d93c06b4"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("inv_compras")}
    if "fecha_factura" not in cols:
        with op.batch_alter_table("inv_compras", schema=None) as batch_op:
            batch_op.add_column(sa.Column("fecha_factura", sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        batch_op.drop_column("fecha_factura")
