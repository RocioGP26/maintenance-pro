"""Catálogo y versionado de procedimientos de mantenimiento.

Revision ID: gm5d1f37k60v
Revises: fl4c0e26j49u
"""

from alembic import op
import sqlalchemy as sa


revision = "gm5d1f37k60v"
down_revision = "fl4c0e26j49u"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "maintenance_procedures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=48), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("machine_type_id", sa.Integer(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["machine_type_id"], ["machine_types.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("empresa_id", "code", name="uq_maintenance_procedure_tenant_code"),
    )
    op.create_index("ix_maintenance_procedures_empresa_id", "maintenance_procedures", ["empresa_id"])
    op.create_index("ix_maintenance_procedures_machine_type_id", "maintenance_procedures", ["machine_type_id"])

    op.create_table(
        "maintenance_procedure_versions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("procedure_id", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("change_notes", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("published_by_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("published_at", sa.DateTime(), nullable=True),
        sa.Column("retired_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint("version > 0", name="ck_maintenance_procedure_version_positive"),
        sa.CheckConstraint(
            "status in ('draft', 'published', 'retired')",
            name="ck_maintenance_procedure_version_status",
        ),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["procedure_id"], ["maintenance_procedures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["published_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("procedure_id", "version", name="uq_maintenance_procedure_version"),
    )
    op.create_index("ix_maintenance_procedure_versions_procedure_id", "maintenance_procedure_versions", ["procedure_id"])

    op.create_table(
        "maintenance_procedure_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=48), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False, server_default=""),
        sa.Column("response_type", sa.String(length=24), nullable=False, server_default="confirmation"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("config_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("position > 0", name="ck_maintenance_procedure_step_position_positive"),
        sa.ForeignKeyConstraint(["version_id"], ["maintenance_procedure_versions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("version_id", "code", name="uq_maintenance_procedure_step_code"),
        sa.UniqueConstraint("version_id", "position", name="uq_maintenance_procedure_step_position"),
    )
    op.create_index("ix_maintenance_procedure_steps_version_id", "maintenance_procedure_steps", ["version_id"])

    op.create_table(
        "maintenance_procedure_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("procedure_id", sa.Integer(), nullable=False),
        sa.Column("version_id", sa.Integer(), nullable=True),
        sa.Column("event", sa.String(length=48), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("previous_status", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("new_status", sa.String(length=20), nullable=False, server_default=""),
        sa.Column("detail", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["procedure_id"], ["maintenance_procedures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_id"], ["maintenance_procedure_versions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_maintenance_procedure_events_created_at", "maintenance_procedure_events", ["created_at"])
    op.create_index("ix_maintenance_procedure_events_empresa_id", "maintenance_procedure_events", ["empresa_id"])
    op.create_index("ix_maintenance_procedure_events_event", "maintenance_procedure_events", ["event"])
    op.create_index("ix_maintenance_procedure_events_procedure_id", "maintenance_procedure_events", ["procedure_id"])
    op.create_index("ix_maintenance_procedure_events_version_id", "maintenance_procedure_events", ["version_id"])


def downgrade():
    op.drop_table("maintenance_procedure_events")
    op.drop_table("maintenance_procedure_steps")
    op.drop_table("maintenance_procedure_versions")
    op.drop_table("maintenance_procedures")
