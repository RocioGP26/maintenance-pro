"""Agrega herramientas y snapshot de costo de repuestos en OT.

Revision ID: bh1y6a82f05q
Revises: ag0x5z71e94p
"""

from alembic import op
import sqlalchemy as sa


revision = "bh1y6a82f05q"
down_revision = "ag0x5z71e94p"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("work_orders") as batch_op:
        batch_op.add_column(
            sa.Column(
                "costo_herramientas",
                sa.Numeric(precision=14, scale=2),
                nullable=False,
                server_default="0",
            )
        )
    with op.batch_alter_table("work_order_repuestos") as batch_op:
        batch_op.add_column(
            sa.Column("costo_unitario_aplicado", sa.Numeric(precision=14, scale=2), nullable=True)
        )
    op.execute(
        """
        UPDATE work_order_repuestos
        SET costo_unitario_aplicado = (
            SELECT spare_parts.costo_unitario
            FROM spare_parts
            WHERE spare_parts.id = work_order_repuestos.spare_part_id
        )
        WHERE costo_unitario_aplicado IS NULL
        """
    )


def downgrade():
    with op.batch_alter_table("work_order_repuestos") as batch_op:
        batch_op.drop_column("costo_unitario_aplicado")
    with op.batch_alter_table("work_orders") as batch_op:
        batch_op.drop_column("costo_herramientas")
