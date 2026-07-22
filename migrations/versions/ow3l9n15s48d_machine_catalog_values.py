"""Catálogo técnico de activos (marca, modelo, fabricante).

Revision ID: ow3l9n15s48d
Revises: nu2k8m04r37c
"""

from alembic import op
import sqlalchemy as sa


revision = "ow3l9n15s48d"
down_revision = "nu2k8m04r37c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "machine_catalog_values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("campo", sa.String(length=32), nullable=False),
        sa.Column("valor", sa.String(length=120), nullable=False),
        sa.Column("valor_norm", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "empresa_id",
            "campo",
            "valor_norm",
            name="uq_machine_catalog_empresa_campo_valor",
        ),
    )
    op.create_index(
        "ix_machine_catalog_values_empresa_id", "machine_catalog_values", ["empresa_id"]
    )
    op.create_index("ix_machine_catalog_values_campo", "machine_catalog_values", ["campo"])


def downgrade():
    op.drop_index("ix_machine_catalog_values_campo", table_name="machine_catalog_values")
    op.drop_index("ix_machine_catalog_values_empresa_id", table_name="machine_catalog_values")
    op.drop_table("machine_catalog_values")
