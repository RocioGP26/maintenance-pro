"""tipo_codigo en preventive_maintenance_plans

Revision ID: tb8q4s60x93i_cronograma_tipo
Revises: sa7p3r59w82h
Create Date: 2026-07-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "tb8q4s60x93i_cronograma_tipo"
down_revision = "sa7p3r59w82h"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("preventive_maintenance_plans") as batch:
        batch.add_column(
            sa.Column("tipo_codigo", sa.String(length=8), nullable=False, server_default="I")
        )


def downgrade() -> None:
    with op.batch_alter_table("preventive_maintenance_plans") as batch:
        batch.drop_column("tipo_codigo")
