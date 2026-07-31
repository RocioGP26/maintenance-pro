"""Encrypted transactional email outbox.

Revision ID: rt9u4v06w18y_email_outbox
Revises: qs8t3u95v17x_storage_addon
"""

from alembic import op
import sqlalchemy as sa


revision = "rt9u4v06w18y_email_outbox"
down_revision = "qs8t3u95v17x_storage_addon"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "email_outbox",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("kind", sa.String(length=40), nullable=False),
        sa.Column("idempotency_key", sa.String(length=160), nullable=False),
        sa.Column("payload_sealed", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("max_attempts", sa.Integer(), nullable=False),
        sa.Column("next_attempt_at", sa.DateTime(), nullable=False),
        sa.Column("lease_expires_at", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.String(length=120), nullable=True),
        sa.Column("source_type", sa.String(length=40), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "empresa_id", "idempotency_key", name="uq_email_outbox_tenant_idempotency"
        ),
    )
    for column in (
        "empresa_id",
        "kind",
        "status",
        "next_attempt_at",
        "lease_expires_at",
        "sent_at",
        "created_at",
    ):
        op.create_index(f"ix_email_outbox_{column}", "email_outbox", [column])


def downgrade():
    op.drop_table("email_outbox")
