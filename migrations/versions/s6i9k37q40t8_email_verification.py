"""Agrega verificación segura de correo para tenants.

Revision ID: s6i9k37q40t8
Revises: r5h8j26p39s7
"""

from alembic import op
import sqlalchemy as sa


revision = "s6i9k37q40t8"
down_revision = "r5h8j26p39s7"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.add_column(sa.Column("email_verified_at", sa.DateTime(), nullable=True))

    # No bloquea tenants creados antes de esta funcionalidad.
    op.execute(
        "UPDATE empresas SET email_verified_at = "
        "COALESCE(fecha_registro, CURRENT_TIMESTAMP)"
    )

    op.create_table(
        "email_verifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("code_hash", sa.String(length=256), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_verifications_empresa_id", "email_verifications", ["empresa_id"])
    op.create_index("ix_email_verifications_user_id", "email_verifications", ["user_id"])
    op.create_index("ix_email_verifications_email", "email_verifications", ["email"])
    op.create_index("ix_email_verifications_expires_at", "email_verifications", ["expires_at"])
    op.create_index("ix_email_verifications_used_at", "email_verifications", ["used_at"])


def downgrade():
    op.drop_index("ix_email_verifications_used_at", table_name="email_verifications")
    op.drop_index("ix_email_verifications_expires_at", table_name="email_verifications")
    op.drop_index("ix_email_verifications_email", table_name="email_verifications")
    op.drop_index("ix_email_verifications_user_id", table_name="email_verifications")
    op.drop_index("ix_email_verifications_empresa_id", table_name="email_verifications")
    op.drop_table("email_verifications")
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.drop_column("email_verified_at")
