"""Disparadores y automatizaciones configurables.

Revision ID: ls0i6k82p15a
Revises: kr9h5j71o04z
"""
from alembic import op
import sqlalchemy as sa


revision = "ls0i6k82p15a"
down_revision = "kr9h5j71o04z"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "maintenance_automation_rules",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(160), nullable=False), sa.Column("description", sa.String(500), nullable=False, server_default=""),
        sa.Column("trigger_type", sa.String(32), nullable=False, server_default="meter_threshold"),
        sa.Column("meter_id", sa.Integer(), nullable=False), sa.Column("operator", sa.String(8), nullable=False),
        sa.Column("threshold", sa.Numeric(20, 6), nullable=False), sa.Column("crossing_only", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("cooldown_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("action_type", sa.String(32), nullable=False), sa.Column("action_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("trigger_type in ('meter_threshold')", name="ck_maintenance_automation_trigger"),
        sa.CheckConstraint("operator in ('gt','gte','lt','lte')", name="ck_maintenance_automation_operator"),
        sa.CheckConstraint("action_type in ('notify','create_work_order')", name="ck_maintenance_automation_action"),
        sa.CheckConstraint("cooldown_minutes >= 0", name="ck_maintenance_automation_cooldown"),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["meter_id"], ["asset_meters.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("empresa_id", "name", name="uq_maintenance_automation_tenant_name"),
    )
    for column in ("empresa_id", "meter_id"):
        op.create_index(f"ix_maintenance_automation_rules_{column}", "maintenance_automation_rules", [column])

    op.create_table(
        "maintenance_automation_executions",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False), sa.Column("reading_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False), sa.Column("matched", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reason", sa.String(120), nullable=False, server_default=""),
        sa.Column("condition_snapshot", sa.String(500), nullable=False, server_default=""),
        sa.Column("action_snapshot", sa.String(500), nullable=False, server_default=""),
        sa.Column("work_order_id", sa.Integer(), nullable=True), sa.Column("error", sa.String(500), nullable=False, server_default=""),
        sa.Column("evaluated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("status in ('succeeded','skipped','failed')", name="ck_maintenance_automation_execution_status"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reading_id"], ["meter_readings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rule_id"], ["maintenance_automation_rules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("rule_id", "reading_id", name="uq_maintenance_automation_rule_reading"),
    )
    for column in ("empresa_id", "rule_id", "reading_id", "work_order_id", "evaluated_at"):
        op.create_index(f"ix_maintenance_automation_executions_{column}", "maintenance_automation_executions", [column])

    op.create_table(
        "maintenance_automation_notifications",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("execution_id", sa.Integer(), nullable=False), sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(180), nullable=False), sa.Column("message", sa.String(500), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["execution_id"], ["maintenance_automation_executions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("execution_id", "user_id", name="uq_maintenance_automation_notification_user"),
    )
    for column in ("empresa_id", "execution_id", "user_id", "read_at", "created_at"):
        op.create_index(f"ix_maintenance_automation_notifications_{column}", "maintenance_automation_notifications", [column])

    op.create_table(
        "maintenance_automation_events",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=False), sa.Column("execution_id", sa.Integer(), nullable=True),
        sa.Column("event", sa.String(64), nullable=False), sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("detail", sa.String(500), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["execution_id"], ["maintenance_automation_executions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["rule_id"], ["maintenance_automation_rules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    for column in ("empresa_id", "rule_id", "execution_id", "event", "created_at"):
        op.create_index(f"ix_maintenance_automation_events_{column}", "maintenance_automation_events", [column])


def downgrade():
    op.drop_table("maintenance_automation_events")
    op.drop_table("maintenance_automation_notifications")
    op.drop_table("maintenance_automation_executions")
    op.drop_table("maintenance_automation_rules")
