"""inv_compra pagos cuentas por pagar

Revision ID: h5d8f26f39e7
Revises: g4c7e15e28d6
Create Date: 2026-07-04 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "h5d8f26f39e7"
down_revision = "g4c7e15e28d6"
branch_labels = None
depends_on = None


def upgrade():
    from sqlalchemy import inspect

    bind = op.get_bind()
    compra_cols = {c["name"] for c in inspect(bind).get_columns("inv_compras")}
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        if "estado_pago" not in compra_cols:
            batch_op.add_column(
                sa.Column("estado_pago", sa.String(length=16), nullable=True, server_default="pendiente")
            )
        if "monto_pagado" not in compra_cols:
            batch_op.add_column(
                sa.Column("monto_pagado", sa.Float(), nullable=True, server_default="0")
            )

    if not inspect(bind).has_table("inv_compra_pagos"):
        op.create_table(
            "inv_compra_pagos",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("compra_id", sa.Integer(), nullable=False),
            sa.Column("monto", sa.Float(), nullable=False),
            sa.Column("fecha", sa.Date(), nullable=False),
            sa.Column("cuenta_origen", sa.String(length=120), nullable=True),
            sa.Column("numero_comprobante", sa.String(length=64), nullable=True),
            sa.Column("notas", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["compra_id"], ["inv_compras.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        with op.batch_alter_table("inv_compra_pagos", schema=None) as batch_op:
            batch_op.create_index(batch_op.f("ix_inv_compra_pagos_compra_id"), ["compra_id"], unique=False)

    op.execute(
        "UPDATE inv_compras SET estado_pago = 'pendiente', monto_pagado = 0 "
        "WHERE (estado_pago IS NULL OR estado_pago = '') AND total > 0"
    )
    op.execute(
        "UPDATE inv_compras SET estado_pago = 'pagada', monto_pagado = 0 "
        "WHERE (estado_pago IS NULL OR estado_pago = '') AND (total IS NULL OR total <= 0)"
    )


def downgrade():
    op.drop_table("inv_compra_pagos")
    with op.batch_alter_table("inv_compras", schema=None) as batch_op:
        batch_op.drop_column("monto_pagado")
        batch_op.drop_column("estado_pago")
