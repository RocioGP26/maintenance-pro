"""inv_producto subcategoria

Revision ID: b7e4f1a92c03
Revises: a6dc612735e8
Create Date: 2026-06-28 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "b7e4f1a92c03"
down_revision = "a6dc612735e8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("inv_productos", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("subcategoria", sa.String(length=120), nullable=True, server_default="")
        )


def downgrade():
    with op.batch_alter_table("inv_productos", schema=None) as batch_op:
        batch_op.drop_column("subcategoria")
