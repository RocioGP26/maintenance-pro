"""Agrega informes técnicos adjuntos a las órdenes de trabajo.

Revision ID: a4r9t15y38b6
Revises: ad7u2w48b61e9
"""
from alembic import op
import sqlalchemy as sa


revision = "a4r9t15y38b6"
down_revision = "ad7u2w48b61e9"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    if "work_order_informes" not in inspector.get_table_names():
        op.create_table(
            "work_order_informes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
            sa.Column("work_order_id", sa.Integer(), sa.ForeignKey("work_orders.id", ondelete="CASCADE"), nullable=False),
            sa.Column("nombre_original", sa.String(255), nullable=False),
            sa.Column("ruta_archivo", sa.String(500), nullable=False),
            sa.Column("descripcion", sa.String(255), nullable=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=False),
        )
        op.create_index("ix_work_order_informes_empresa_id", "work_order_informes", ["empresa_id"])
        op.create_index("ix_work_order_informes_work_order_id", "work_order_informes", ["work_order_id"])


def downgrade():
    inspector = sa.inspect(op.get_bind())
    if "work_order_informes" in inspector.get_table_names():
        op.drop_table("work_order_informes")
