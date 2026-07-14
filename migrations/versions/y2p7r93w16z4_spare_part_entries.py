"""Agrega historial de compras y entradas de repuestos técnicos.

Revision ID: y2p7r93w16z4
Revises: x1n6q82v05y3
"""
from alembic import op
import sqlalchemy as sa


revision = "y2p7r93w16z4"
down_revision = "x1n6q82v05y3"
branch_labels = None
depends_on = None


def upgrade():
    tables = set(sa.inspect(op.get_bind()).get_table_names())
    if "spare_part_entries" not in tables:
        op.create_table(
            "spare_part_entries",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
            sa.Column("spare_part_id", sa.Integer(), sa.ForeignKey("spare_parts.id"), nullable=False),
            sa.Column("cantidad", sa.Integer(), nullable=False),
            sa.Column("costo_unitario", sa.Float(), nullable=False, server_default="0"),
            sa.Column("fecha_compra", sa.Date(), nullable=False),
            sa.Column("proveedor_id", sa.Integer(), sa.ForeignKey("proveedores.id"), nullable=True),
            sa.Column("numero_factura", sa.String(80), nullable=True),
            sa.Column("notas", sa.Text(), nullable=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_spare_part_entries_empresa_id", "spare_part_entries", ["empresa_id"])
        op.create_index("ix_spare_part_entries_spare_part_id", "spare_part_entries", ["spare_part_id"])


def downgrade():
    op.drop_table("spare_part_entries")
