"""Tabla password_resets para restablecimiento self-service.

Revision ID: pr7s2t84u06w_password_resets
Revises: tb8q4s60x93i_cronograma_tipo
Create Date: 2026-07-27
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "pr7s2t84u06w_password_resets"
down_revision = "tb8q4s60x93i_cronograma_tipo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_resets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("used_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_password_resets_empresa_id", "password_resets", ["empresa_id"])
    op.create_index("ix_password_resets_user_id", "password_resets", ["user_id"])
    op.create_index("ix_password_resets_email", "password_resets", ["email"])
    op.create_index("ix_password_resets_token_hash", "password_resets", ["token_hash"], unique=True)
    op.create_index("ix_password_resets_expires_at", "password_resets", ["expires_at"])
    op.create_index("ix_password_resets_used_at", "password_resets", ["used_at"])


def downgrade() -> None:
    op.drop_index("ix_password_resets_used_at", table_name="password_resets")
    op.drop_index("ix_password_resets_expires_at", table_name="password_resets")
    op.drop_index("ix_password_resets_token_hash", table_name="password_resets")
    op.drop_index("ix_password_resets_email", table_name="password_resets")
    op.drop_index("ix_password_resets_user_id", table_name="password_resets")
    op.drop_index("ix_password_resets_empresa_id", table_name="password_resets")
    op.drop_table("password_resets")
