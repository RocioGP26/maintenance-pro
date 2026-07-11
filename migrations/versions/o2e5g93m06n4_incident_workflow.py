"""incident operational workflow

Revision ID: o2e5g93m06n4
Revises: n1d4f82l95k3
"""
from alembic import op
import sqlalchemy as sa

revision = "o2e5g93m06n4"
down_revision = "n1d4f82l95k3"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incidents") as b:
        b.add_column(sa.Column("area_responsable", sa.String(120), nullable=False, server_default="Mantenimiento"))
        b.add_column(sa.Column("prioridad_confirmada", sa.String(32), server_default=""))
        b.add_column(sa.Column("estado", sa.String(32), nullable=False, server_default="reportado"))
        b.add_column(sa.Column("responsable_area_id", sa.Integer(), nullable=True))
        b.add_column(sa.Column("tecnico_asignado_id", sa.Integer(), nullable=True))
        b.add_column(sa.Column("recibido_en", sa.DateTime(), nullable=True))
        b.add_column(sa.Column("asignado_en", sa.DateTime(), nullable=True))
        b.add_column(sa.Column("iniciado_en", sa.DateTime(), nullable=True))
        b.add_column(sa.Column("diagnosticado_en", sa.DateTime(), nullable=True))
        b.add_column(sa.Column("cerrado_en", sa.DateTime(), nullable=True))
        b.add_column(sa.Column("motivo_cierre", sa.Text(), server_default=""))
        b.create_index("ix_incidents_estado", ["estado"])
        b.create_foreign_key("fk_incident_responsable", "users", ["responsable_area_id"], ["id"])
        b.create_foreign_key("fk_incident_tecnico", "technicians", ["tecnico_asignado_id"], ["id"])
    op.create_table("incident_diagnoses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("technician_id", sa.Integer(), sa.ForeignKey("technicians.id")),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("hallazgo", sa.Text(), nullable=False),
        sa.Column("causa", sa.Text()), sa.Column("pruebas", sa.Text()), sa.Column("recomendacion", sa.Text()),
        sa.Column("resultado", sa.String(32), nullable=False), sa.Column("evidencia", sa.Text()))
    op.create_table("incident_history",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("incident_id", sa.Integer(), sa.ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id")), sa.Column("accion", sa.String(80), nullable=False),
        sa.Column("estado_anterior", sa.String(32)), sa.Column("estado_nuevo", sa.String(32)),
        sa.Column("comentario", sa.Text()), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.execute("UPDATE incidents SET estado = CASE WHEN resuelto = 1 THEN 'resuelto' ELSE 'reportado' END")


def downgrade():
    op.drop_table("incident_history")
    op.drop_table("incident_diagnoses")
    with op.batch_alter_table("incidents") as b:
        b.drop_constraint("fk_incident_tecnico", type_="foreignkey")
        b.drop_constraint("fk_incident_responsable", type_="foreignkey")
        b.drop_index("ix_incidents_estado")
        for name in ("motivo_cierre", "cerrado_en", "diagnosticado_en", "iniciado_en", "asignado_en", "recibido_en", "tecnico_asignado_id", "responsable_area_id", "estado", "prioridad_confirmada", "area_responsable"):
            b.drop_column(name)
