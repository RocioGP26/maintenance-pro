"""purchasing vinculo recepcion cxp

Revision ID: n1d4f82l95k3
Revises: m0c3e71k84j2
"""
from alembic import op
import sqlalchemy as sa

revision = "n1d4f82l95k3"
down_revision = "m0c3e71k84j2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("pur_recepciones") as batch_op:
        batch_op.add_column(sa.Column("inv_compra_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_pur_recepcion_inv_compra", "inv_compras", ["inv_compra_id"], ["id"])
        batch_op.create_unique_constraint("uq_pur_recepcion_inv_compra", ["inv_compra_id"])
    op.create_index("ix_pur_recepciones_inv_compra_id", "pur_recepciones", ["inv_compra_id"])


def downgrade():
    op.drop_index("ix_pur_recepciones_inv_compra_id", table_name="pur_recepciones")
    with op.batch_alter_table("pur_recepciones") as batch_op:
        batch_op.drop_constraint("uq_pur_recepcion_inv_compra", type_="unique")
        batch_op.drop_constraint("fk_pur_recepcion_inv_compra", type_="foreignkey")
        batch_op.drop_column("inv_compra_id")
