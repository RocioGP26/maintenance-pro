"""Gestión de sesiones y política de seguridad por tenant.

Revision ID: t7j0l48r51u9
Revises: s6i9k37q40t8
"""

from alembic import op
import sqlalchemy as sa


revision = "t7j0l48r51u9"
down_revision = "s6i9k37q40t8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.add_column(sa.Column("session_idle_minutes", sa.Integer(), nullable=False, server_default="30"))
        batch_op.add_column(sa.Column("session_absolute_minutes", sa.Integer(), nullable=False, server_default="480"))
        batch_op.add_column(sa.Column("session_remember_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("session_warning_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("session_warning_minutes", sa.Integer(), nullable=False, server_default="2"))
        batch_op.add_column(sa.Column("session_revoke_on_password", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("session_allow_multiple", sa.Boolean(), nullable=False, server_default=sa.true()))

    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("auth_version", sa.Integer(), nullable=False, server_default="1"))

    op.create_table(
        "active_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_key", sa.String(length=36), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_reason", sa.String(length=80), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("remember", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_key"),
    )
    for column in ("session_key", "empresa_id", "user_id", "last_activity_at", "absolute_expires_at", "revoked_at"):
        op.create_index(f"ix_active_sessions_{column}", "active_sessions", [column])


def downgrade():
    for column in ("revoked_at", "absolute_expires_at", "last_activity_at", "user_id", "empresa_id", "session_key"):
        op.drop_index(f"ix_active_sessions_{column}", table_name="active_sessions")
    op.drop_table("active_sessions")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("auth_version")
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.drop_column("session_allow_multiple")
        batch_op.drop_column("session_revoke_on_password")
        batch_op.drop_column("session_warning_minutes")
        batch_op.drop_column("session_warning_enabled")
        batch_op.drop_column("session_remember_enabled")
        batch_op.drop_column("session_absolute_minutes")
        batch_op.drop_column("session_idle_minutes")
