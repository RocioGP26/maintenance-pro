"""Asset Health avanzado e historial de snapshots.

Revision ID: nu2k8m04r37c
Revises: mt1j7l93q26b
"""

from alembic import op
import sqlalchemy as sa


revision = "nu2k8m04r37c"
down_revision = "mt1j7l93q26b"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "asset_health_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("machine_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Integer(), nullable=False),
        sa.Column("band", sa.String(16), nullable=False),
        sa.Column("factors_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("reasons_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("trigger", sa.String(48), nullable=False, server_default="manual"),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("calculated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("score >= 0 and score <= 100", name="ck_asset_health_score"),
        sa.CheckConstraint("confidence >= 0 and confidence <= 100", name="ck_asset_health_confidence"),
        sa.CheckConstraint("band in ('healthy','watch','at_risk','critical','unknown')", name="ck_asset_health_band"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asset_health_snapshots_empresa_id", "asset_health_snapshots", ["empresa_id"])
    op.create_index("ix_asset_health_snapshots_machine_id", "asset_health_snapshots", ["machine_id"])
    op.create_index("ix_asset_health_snapshots_band", "asset_health_snapshots", ["band"])
    op.create_index("ix_asset_health_snapshots_calculated_at", "asset_health_snapshots", ["calculated_at"])


def downgrade():
    op.drop_index("ix_asset_health_snapshots_calculated_at", table_name="asset_health_snapshots")
    op.drop_index("ix_asset_health_snapshots_band", table_name="asset_health_snapshots")
    op.drop_index("ix_asset_health_snapshots_machine_id", table_name="asset_health_snapshots")
    op.drop_index("ix_asset_health_snapshots_empresa_id", table_name="asset_health_snapshots")
    op.drop_table("asset_health_snapshots")
