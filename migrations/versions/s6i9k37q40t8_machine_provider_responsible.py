"""Relaciona activos con proveedores y datos del responsable.

Revision ID: s6i9k37q40t8
Revises: p3f6h04n17q5
"""
from alembic import op
import sqlalchemy as sa


revision = "s6i9k37q40t8"
down_revision = "p3f6h04n17q5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("machines") as batch_op:
        batch_op.add_column(sa.Column("proveedor_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("responsable_area", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("responsable_cargo", sa.String(length=120), nullable=True))
        batch_op.create_index("ix_machines_proveedor_id", ["proveedor_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_machines_proveedor_id_proveedores",
            "proveedores",
            ["proveedor_id"],
            ["id"],
        )

    op.execute(
        """
        UPDATE machines
        SET proveedor_id = (
            SELECT p.id
            FROM proveedores p
            WHERE p.empresa_id = machines.empresa_id
              AND lower(trim(p.nombre)) = lower(trim(machines.proveedor))
            ORDER BY p.activo DESC, p.id
            LIMIT 1
        )
        WHERE trim(coalesce(machines.proveedor, '')) <> ''
        """
    )


def downgrade():
    with op.batch_alter_table("machines") as batch_op:
        batch_op.drop_constraint("fk_machines_proveedor_id_proveedores", type_="foreignkey")
        batch_op.drop_index("ix_machines_proveedor_id")
        batch_op.drop_column("responsable_cargo")
        batch_op.drop_column("responsable_area")
        batch_op.drop_column("proveedor_id")
