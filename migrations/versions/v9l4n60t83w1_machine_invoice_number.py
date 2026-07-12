"""Agrega número de factura a la información financiera del activo.

Revision ID: v9l4n60t83w1
Revises: u8k3m59s72v0
"""
from alembic import op
import sqlalchemy as sa


revision = "v9l4n60t83w1"
down_revision = "u8k3m59s72v0"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("machines")}
    if "numero_factura" not in columns:
        with op.batch_alter_table("machines") as batch_op:
            batch_op.add_column(sa.Column("numero_factura", sa.String(length=80), nullable=True))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("machines")}
    if "numero_factura" in columns:
        with op.batch_alter_table("machines") as batch_op:
            batch_op.drop_column("numero_factura")
