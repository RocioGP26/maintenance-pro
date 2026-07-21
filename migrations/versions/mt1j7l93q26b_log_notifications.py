"""Alertas de bitácora contextual y validación de cierre de OT.

Revision ID: mt1j7l93q26b
Revises: ls0i6k82p15a
"""

from alembic import op
import sqlalchemy as sa


revision = "mt1j7l93q26b"
down_revision = "ls0i6k82p15a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "maintenance_log_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entry_id"], ["maintenance_log_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("entry_id", "user_id", name="uq_maintenance_log_notification_user"),
    )
    op.create_index("ix_maintenance_log_notifications_empresa_id", "maintenance_log_notifications", ["empresa_id"])
    op.create_index("ix_maintenance_log_notifications_entry_id", "maintenance_log_notifications", ["entry_id"])
    op.create_index("ix_maintenance_log_notifications_user_id", "maintenance_log_notifications", ["user_id"])
    op.create_index("ix_maintenance_log_notifications_read_at", "maintenance_log_notifications", ["read_at"])
    op.create_index("ix_maintenance_log_notifications_created_at", "maintenance_log_notifications", ["created_at"])


def downgrade():
    op.drop_index("ix_maintenance_log_notifications_created_at", table_name="maintenance_log_notifications")
    op.drop_index("ix_maintenance_log_notifications_read_at", table_name="maintenance_log_notifications")
    op.drop_index("ix_maintenance_log_notifications_user_id", table_name="maintenance_log_notifications")
    op.drop_index("ix_maintenance_log_notifications_entry_id", table_name="maintenance_log_notifications")
    op.drop_index("ix_maintenance_log_notifications_empresa_id", table_name="maintenance_log_notifications")
    op.drop_table("maintenance_log_notifications")
