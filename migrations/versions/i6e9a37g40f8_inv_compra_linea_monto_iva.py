"""inv_compra_linea monto_iva por producto

Revision ID: i6e9a37g40f8
Revises: h5d8f26f39e7
Create Date: 2026-07-05 18:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "i6e9a37g40f8"
down_revision = "h5d8f26f39e7"
branch_labels = None
depends_on = None

IVA_TASA = 0.19


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("inv_compra_lineas")}
    if "monto_iva" not in cols:
        with op.batch_alter_table("inv_compra_lineas", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("monto_iva", sa.Float(), nullable=True, server_default="0")
            )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE inv_compra_lineas
            SET monto_iva = ROUND(CAST(subtotal * :tasa AS numeric), 2)
            WHERE (monto_iva IS NULL OR monto_iva = 0)
              AND compra_id IN (
                SELECT id FROM inv_compras WHERE LOWER(COALESCE(tipo_iva, '')) = 'con_iva'
              )
            """
        ),
        {"tasa": IVA_TASA},
    )


def downgrade():
    with op.batch_alter_table("inv_compra_lineas", schema=None) as batch_op:
        batch_op.drop_column("monto_iva")
