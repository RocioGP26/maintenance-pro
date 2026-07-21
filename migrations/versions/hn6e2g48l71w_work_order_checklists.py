"""Checklist ejecutable asociado a órdenes de trabajo.

Revision ID: hn6e2g48l71w
Revises: gm5d1f37k60v
"""

from alembic import op
import sqlalchemy as sa

revision = "hn6e2g48l71w"
down_revision = "gm5d1f37k60v"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "work_order_checklists",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("work_order_id", sa.Integer(), nullable=False),
        sa.Column("procedure_version_id", sa.Integer(), nullable=False),
        sa.Column("assigned_technician_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("procedure_code_snapshot", sa.String(48), nullable=False),
        sa.Column("procedure_name_snapshot", sa.String(160), nullable=False),
        sa.Column("version_snapshot", sa.Integer(), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("status in ('pending','in_progress','blocked','completed','reviewed','void')", name="ck_work_order_checklist_status"),
        sa.ForeignKeyConstraint(["assigned_technician_id"], ["technicians.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["procedure_version_id"], ["maintenance_procedure_versions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("work_order_id", name="uq_work_order_checklist_order"),
    )
    for column in ("empresa_id", "work_order_id", "procedure_version_id", "assigned_technician_id"):
        op.create_index(f"ix_work_order_checklists_{column}", "work_order_checklists", [column])

    op.create_table(
        "work_order_checklist_responses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("step_id", sa.Integer(), nullable=False),
        sa.Column("value_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("performed_by_user_id", sa.Integer(), nullable=False),
        sa.Column("recorded_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["checklist_id"], ["work_order_checklists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["step_id"], ["maintenance_procedure_steps.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("checklist_id", "step_id", name="uq_checklist_response_step"),
    )
    op.create_index("ix_work_order_checklist_responses_checklist_id", "work_order_checklist_responses", ["checklist_id"])
    op.create_index("ix_work_order_checklist_responses_step_id", "work_order_checklist_responses", ["step_id"])

    op.create_table(
        "work_order_checklist_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("event", sa.String(48), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("detail", sa.String(500), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["checklist_id"], ["work_order_checklists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("empresa_id", "checklist_id", "event", "created_at"):
        op.create_index(f"ix_work_order_checklist_events_{column}", "work_order_checklist_events", [column])


def downgrade():
    op.drop_table("work_order_checklist_events")
    op.drop_table("work_order_checklist_responses")
    op.drop_table("work_order_checklists")
