"""inv_compra_linea tasa_iva porcentaje

Revision ID: j7f0b48h51g9
Revises: i6e9a37g40f8
Create Date: 2026-07-05 19:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "j7f0b48h51g9"
down_revision = "i6e9a37g40f8"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    cols = {c["name"] for c in inspect(bind).get_columns("inv_compra_lineas")}
    if "tasa_iva" not in cols:
        with op.batch_alter_table("inv_compra_lineas", schema=None) as batch_op:
            batch_op.add_column(
                sa.Column("tasa_iva", sa.Float(), nullable=True, server_default="0")
            )

    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE inv_compra_lineas
            SET tasa_iva = CASE
                WHEN subtotal > 0 AND monto_iva > 0
                  THEN ROUND(CAST(monto_iva / subtotal * 100.0 AS numeric), 2)
                ELSE 19.0
            END
            WHERE (tasa_iva IS NULL OR tasa_iva = 0)
              AND compra_id IN (
                SELECT id FROM inv_compras WHERE LOWER(COALESCE(tipo_iva, '')) = 'con_iva'
              )
            """
        )
    )


def downgrade():
    with op.batch_alter_table("inv_compra_lineas", schema=None) as batch_op:
        batch_op.drop_column("tasa_iva")
