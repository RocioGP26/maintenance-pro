"""purchasing solicitudes y auditoria

Revision ID: k8a1c59i62h0
Revises: j7f0b48h51g9
Create Date: 2026-07-11 09:30:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "k8a1c59i62h0"
down_revision = "j7f0b48h51g9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pur_solicitudes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("numero", sa.String(32), nullable=False),
        sa.Column("solicitante_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False, server_default="borrador"),
        sa.Column("prioridad", sa.String(16), nullable=False, server_default="media"),
        sa.Column("justificacion", sa.Text(), nullable=False, server_default=""),
        sa.Column("requerida_para", sa.Date(), nullable=True),
        sa.Column("aprobador_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("decision_en", sa.DateTime(), nullable=True),
        sa.Column("motivo_decision", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("empresa_id", "numero", name="uq_pur_solicitud_empresa_numero"),
    )
    op.create_index("ix_pur_solicitudes_empresa_id", "pur_solicitudes", ["empresa_id"])
    op.create_index("ix_pur_solicitudes_estado", "pur_solicitudes", ["estado"])
    op.create_table(
        "pur_solicitud_lineas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("solicitud_id", sa.Integer(), sa.ForeignKey("pur_solicitudes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("inv_productos.id"), nullable=True),
        sa.Column("descripcion_libre", sa.String(255), nullable=False, server_default=""),
        sa.Column("cantidad", sa.Float(), nullable=False),
        sa.Column("unidad", sa.String(32), nullable=False, server_default="pza"),
        sa.Column("costo_estimado", sa.Float(), nullable=True),
    )
    op.create_index("ix_pur_solicitud_lineas_solicitud_id", "pur_solicitud_lineas", ["solicitud_id"])
    op.create_table(
        "pur_eventos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("solicitud_id", sa.Integer(), sa.ForeignKey("pur_solicitudes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evento", sa.String(32), nullable=False),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("estado_anterior", sa.String(16), nullable=True),
        sa.Column("estado_nuevo", sa.String(16), nullable=False),
        sa.Column("detalle", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_pur_eventos_empresa_id", "pur_eventos", ["empresa_id"])
    op.create_index("ix_pur_eventos_solicitud_id", "pur_eventos", ["solicitud_id"])


def downgrade():
    op.drop_table("pur_eventos")
    op.drop_table("pur_solicitud_lineas")
    op.drop_table("pur_solicitudes")
