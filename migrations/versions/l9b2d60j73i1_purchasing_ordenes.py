"""purchasing ordenes de compra

Revision ID: l9b2d60j73i1
Revises: k8a1c59i62h0
"""
from alembic import op
import sqlalchemy as sa

revision = "l9b2d60j73i1"
down_revision = "k8a1c59i62h0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("pur_ordenes",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("numero", sa.String(32), nullable=False), sa.Column("solicitud_id", sa.Integer(), sa.ForeignKey("pur_solicitudes.id"), nullable=False),
        sa.Column("proveedor_id", sa.Integer(), sa.ForeignKey("inv_proveedores.id"), nullable=False), sa.Column("creador_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False, server_default="borrador"), sa.Column("moneda", sa.String(8), nullable=False, server_default="COP"),
        sa.Column("subtotal", sa.Float(), nullable=False, server_default="0"), sa.Column("monto_iva", sa.Float(), nullable=False, server_default="0"), sa.Column("total", sa.Float(), nullable=False, server_default="0"),
        sa.Column("entrega_prevista", sa.Date(), nullable=True), sa.Column("direccion_entrega", sa.String(255), nullable=False, server_default=""),
        sa.Column("condiciones_pago", sa.String(255), nullable=False, server_default=""), sa.Column("notas", sa.Text(), nullable=False, server_default=""),
        sa.Column("emitida_en", sa.DateTime(), nullable=True), sa.Column("enviada_en", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("empresa_id", "numero", name="uq_pur_orden_empresa_numero"), sa.UniqueConstraint("solicitud_id", name="uq_pur_orden_solicitud"))
    op.create_index("ix_pur_ordenes_empresa_id", "pur_ordenes", ["empresa_id"]); op.create_index("ix_pur_ordenes_estado", "pur_ordenes", ["estado"])
    op.create_table("pur_orden_lineas",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("orden_id", sa.Integer(), sa.ForeignKey("pur_ordenes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("solicitud_linea_id", sa.Integer(), sa.ForeignKey("pur_solicitud_lineas.id"), nullable=False), sa.Column("producto_id", sa.Integer(), sa.ForeignKey("inv_productos.id"), nullable=True),
        sa.Column("descripcion_snapshot", sa.String(255), nullable=False), sa.Column("unidad", sa.String(32), nullable=False), sa.Column("cantidad_ordenada", sa.Float(), nullable=False),
        sa.Column("precio_unitario", sa.Float(), nullable=False, server_default="0"), sa.Column("tasa_iva", sa.Float(), nullable=False, server_default="0"),
        sa.Column("subtotal", sa.Float(), nullable=False, server_default="0"), sa.Column("monto_iva", sa.Float(), nullable=False, server_default="0"), sa.Column("total", sa.Float(), nullable=False, server_default="0"))
    op.create_index("ix_pur_orden_lineas_orden_id", "pur_orden_lineas", ["orden_id"])
    op.create_table("pur_orden_eventos",
        sa.Column("id", sa.Integer(), primary_key=True), sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("orden_id", sa.Integer(), sa.ForeignKey("pur_ordenes.id", ondelete="CASCADE"), nullable=False), sa.Column("evento", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False), sa.Column("estado_anterior", sa.String(16), nullable=True),
        sa.Column("estado_nuevo", sa.String(16), nullable=False), sa.Column("detalle", sa.Text(), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_pur_orden_eventos_orden_id", "pur_orden_eventos", ["orden_id"])


def downgrade():
    op.drop_table("pur_orden_eventos"); op.drop_table("pur_orden_lineas"); op.drop_table("pur_ordenes")
