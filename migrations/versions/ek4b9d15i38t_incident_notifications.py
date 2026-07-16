"""Notificaciones individuales para incidencias.

Revision ID: ek4b9d15i38t
Revises: dj3a8c04h27s
"""

from alembic import op
import sqlalchemy as sa


revision = "ek4b9d15i38t"
down_revision = "dj3a8c04h27s"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "incident_notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("incident_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("shown_at", sa.DateTime(), nullable=True),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("accessed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "incident_id", "user_id", name="uq_incident_notification_user"
        ),
    )
    op.create_index(
        "ix_incident_notifications_empresa_id",
        "incident_notifications",
        ["empresa_id"],
    )
    op.create_index(
        "ix_incident_notifications_incident_id",
        "incident_notifications",
        ["incident_id"],
    )
    op.create_index(
        "ix_incident_notifications_user_id",
        "incident_notifications",
        ["user_id"],
    )
    op.create_index(
        "ix_incident_notifications_shown_at",
        "incident_notifications",
        ["shown_at"],
    )
    op.create_index(
        "ix_incident_notifications_read_at",
        "incident_notifications",
        ["read_at"],
    )
    op.create_index(
        "ix_incident_notifications_created_at",
        "incident_notifications",
        ["created_at"],
    )


def downgrade():
    op.drop_index("ix_incident_notifications_created_at", table_name="incident_notifications")
    op.drop_index("ix_incident_notifications_read_at", table_name="incident_notifications")
    op.drop_index("ix_incident_notifications_shown_at", table_name="incident_notifications")
    op.drop_index("ix_incident_notifications_user_id", table_name="incident_notifications")
    op.drop_index("ix_incident_notifications_incident_id", table_name="incident_notifications")
    op.drop_index("ix_incident_notifications_empresa_id", table_name="incident_notifications")
    op.drop_table("incident_notifications")
