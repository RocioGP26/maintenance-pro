"""Add-on almacenamiento empresas.storage_addon_mb (COM-02 ADD-STG-2G).

Revision ID: qs8t3u95v17x_storage_addon
Revises: pr7s2t84u06w_password_resets
Create Date: 2026-07-29
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "qs8t3u95v17x_storage_addon"
down_revision = "pr7s2t84u06w_password_resets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.add_column(
            sa.Column("storage_addon_mb", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("empresas") as batch_op:
        batch_op.drop_column("storage_addon_mb")
