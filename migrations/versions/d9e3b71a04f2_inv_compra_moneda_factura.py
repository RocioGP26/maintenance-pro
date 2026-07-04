"""inv_compra moneda factura y tasa cambio

Revision ID: d9e3b71a04f2
Revises: c8f2a91d04e1
Create Date: 2026-07-04 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "d9e3b71a04f2"
down_revision = "c8f2a91d04e1"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("inv_compras")}
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        if "moneda_factura" not in cols:
            batch_op.add_column(
                sa.Column("moneda_factura", sa.String(length=8), nullable=True, server_default="COP")
            )
        if "tasa_cambio" not in cols:
            batch_op.add_column(
                sa.Column("tasa_cambio", sa.Float(), nullable=True, server_default="1")
            )


def downgrade():
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        batch_op.drop_column("tasa_cambio")
        batch_op.drop_column("moneda_factura")
