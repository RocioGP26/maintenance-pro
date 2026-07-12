"""purchasing recepciones

Revision ID: m0c3e71k84j2
Revises: l9b2d60j73i1
"""
from alembic import op
import sqlalchemy as sa

revision = "m0c3e71k84j2"
down_revision = "l9b2d60j73i1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("pur_recepciones",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("numero", sa.String(32), nullable=False), sa.Column("orden_id", sa.Integer(), sa.ForeignKey("pur_ordenes.id"), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False, server_default="confirmada"), sa.Column("recibido_por_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("fecha", sa.Date(), nullable=False), sa.Column("idempotency_key", sa.String(64), nullable=False),
        sa.Column("documento_proveedor", sa.String(64), nullable=False, server_default=""), sa.Column("observaciones", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.UniqueConstraint("empresa_id", "numero", name="uq_pur_recepcion_empresa_numero"),
        sa.UniqueConstraint("empresa_id", "idempotency_key", name="uq_pur_recepcion_empresa_idempotency"))
    op.create_index("ix_pur_recepciones_empresa_id", "pur_recepciones", ["empresa_id"]); op.create_index("ix_pur_recepciones_orden_id", "pur_recepciones", ["orden_id"])
    op.create_table("pur_recepcion_lineas",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("recepcion_id", sa.Integer(), sa.ForeignKey("pur_recepciones.id", ondelete="CASCADE"), nullable=False),
        sa.Column("orden_linea_id", sa.Integer(), sa.ForeignKey("pur_orden_lineas.id"), nullable=False), sa.Column("cantidad_recibida", sa.Float(), nullable=False, server_default="0"),
        sa.Column("cantidad_rechazada", sa.Float(), nullable=False, server_default="0"), sa.Column("motivo_rechazo", sa.String(255), nullable=False, server_default=""))
    op.create_index("ix_pur_recepcion_lineas_recepcion_id", "pur_recepcion_lineas", ["recepcion_id"]); op.create_index("ix_pur_recepcion_lineas_orden_linea_id", "pur_recepcion_lineas", ["orden_linea_id"])


def downgrade():
    op.drop_table("pur_recepcion_lineas"); op.drop_table("pur_recepciones")
