"""Agrega requisición a las entradas de repuestos.

Revision ID: z3q8s04x27a5
Revises: y2p7r93w16z4
"""
from alembic import op
import sqlalchemy as sa


revision = "z3q8s04x27a5"
down_revision = "y2p7r93w16z4"
branch_labels = None
depends_on = None


def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("spare_part_entries")}
    if "numero_requisicion" not in columns:
        with op.batch_alter_table("spare_part_entries") as batch_op:
            batch_op.add_column(sa.Column("numero_requisicion", sa.String(80), nullable=True))


def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("spare_part_entries")}
    if "numero_requisicion" in columns:
        with op.batch_alter_table("spare_part_entries") as batch_op:
            batch_op.drop_column("numero_requisicion")
