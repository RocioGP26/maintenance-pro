"""inv_producto ubicacion

Revision ID: c8f2a91d04e1
Revises: b7e4f1a92c03
Create Date: 2026-07-04 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "c8f2a91d04e1"
down_revision = "b7e4f1a92c03"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("inv_productos")}
    if "ubicacion" in cols:
        return
    with op.batch_alter_table("inv_productos", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("ubicacion", sa.String(length=120), nullable=True, server_default="")
        )


def downgrade():
    with op.batch_alter_table("inv_productos", schema=None) as batch_op:
        batch_op.drop_column("ubicacion")
