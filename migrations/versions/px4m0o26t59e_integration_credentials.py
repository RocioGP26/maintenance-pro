"""Credenciales técnicas para API pública.

Revision ID: px4m0o26t59e
Revises: ow3l9n15s48d
"""

from alembic import op
import sqlalchemy as sa


revision = "px4m0o26t59e"
down_revision = "ow3l9n15s48d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "integration_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("key_prefix", sa.String(length=48), nullable=False),
        sa.Column("secret_hash", sa.String(length=256), nullable=False),
        sa.Column("scopes_json", sa.Text(), nullable=False),
        sa.Column("environment", sa.String(length=16), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_used_at", sa.DateTime(), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("rotated_from_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["rotated_from_id"], ["integration_credentials.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key_prefix", name="uq_integration_credentials_key_prefix"),
    )
    for column in ("empresa_id", "key_prefix", "environment", "expires_at", "revoked_at", "created_by_id", "rotated_from_id", "created_at"):
        op.create_index(f"ix_integration_credentials_{column}", "integration_credentials", [column])


def downgrade():
    op.drop_table("integration_credentials")
