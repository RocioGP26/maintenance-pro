"""Separa áreas de soporte, custodio y capacidades de atención.

Revision ID: t7j2k48r61u9
Revises: r5h8j26p39s7
"""
from alembic import op
import sqlalchemy as sa


revision = "t7j2k48r61u9"
down_revision = "r5h8j26p39s7"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "support_areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("empresa_id", sa.Integer(), sa.ForeignKey("empresas.id"), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("empresa_id", "nombre", name="uq_support_area_empresa_nombre"),
    )
    op.create_index("ix_support_areas_empresa_id", "support_areas", ["empresa_id"])
    op.create_table(
        "user_support_areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("support_area_id", sa.Integer(), sa.ForeignKey("support_areas.id"), nullable=False),
        sa.Column("puede_recibir", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("puede_asignar", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("puede_atender", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("puede_diagnosticar", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("user_id", "support_area_id", name="uq_user_support_area"),
    )
    op.create_index("ix_user_support_areas_user_id", "user_support_areas", ["user_id"])
    op.create_index("ix_user_support_areas_support_area_id", "user_support_areas", ["support_area_id"])
    with op.batch_alter_table("machines") as b:
        b.add_column(sa.Column("custodio_user_id", sa.Integer(), nullable=True))
        b.add_column(sa.Column("support_area_id", sa.Integer(), nullable=True))
        b.create_index("ix_machines_custodio_user_id", ["custodio_user_id"])
        b.create_index("ix_machines_support_area_id", ["support_area_id"])
        b.create_foreign_key("fk_machine_custodio", "users", ["custodio_user_id"], ["id"])
        b.create_foreign_key("fk_machine_support_area", "support_areas", ["support_area_id"], ["id"])
    with op.batch_alter_table("incidents") as b:
        b.add_column(sa.Column("support_area_id", sa.Integer(), nullable=True))
        b.create_index("ix_incidents_support_area_id", ["support_area_id"])
        b.create_foreign_key("fk_incident_support_area", "support_areas", ["support_area_id"], ["id"])


def downgrade():
    with op.batch_alter_table("incidents") as b:
        b.drop_constraint("fk_incident_support_area", type_="foreignkey")
        b.drop_index("ix_incidents_support_area_id")
        b.drop_column("support_area_id")
    with op.batch_alter_table("machines") as b:
        b.drop_constraint("fk_machine_support_area", type_="foreignkey")
        b.drop_constraint("fk_machine_custodio", type_="foreignkey")
        b.drop_index("ix_machines_support_area_id")
        b.drop_index("ix_machines_custodio_user_id")
        b.drop_column("support_area_id")
        b.drop_column("custodio_user_id")
    op.drop_table("user_support_areas")
    op.drop_table("support_areas")
