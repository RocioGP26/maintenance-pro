"""Bitácora contextual y adjuntos privados.

Revision ID: jq8g4i60n93y
Revises: ip7f3h59m82x
"""
from alembic import op
import sqlalchemy as sa

revision = "jq8g4i60n93y"
down_revision = "ip7f3h59m82x"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "maintenance_log_entries",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("work_order_id", sa.Integer(), nullable=True), sa.Column("incident_id", sa.Integer(), nullable=True), sa.Column("machine_id", sa.Integer(), nullable=True),
        sa.Column("entry_type", sa.String(32), nullable=False, server_default="comment"),
        sa.Column("visibility", sa.String(16), nullable=False, server_default="internal"),
        sa.Column("body", sa.Text(), nullable=False), sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("performed_by_user_id", sa.Integer(), nullable=True), sa.Column("correction_of_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("(case when work_order_id is not null then 1 else 0 end + case when incident_id is not null then 1 else 0 end + case when machine_id is not null then 1 else 0 end) = 1", name="ck_maintenance_log_single_context"),
        sa.CheckConstraint("visibility in ('internal','requester','system')", name="ck_maintenance_log_visibility"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["correction_of_id"], ["maintenance_log_entries.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["machine_id"], ["machines.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["performed_by_user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"),
    )
    for c in ("empresa_id","work_order_id","incident_id","machine_id","created_at"): op.create_index(f"ix_maintenance_log_entries_{c}", "maintenance_log_entries", [c])
    op.create_table(
        "maintenance_log_attachments",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False), sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False), sa.Column("original_name", sa.String(255), nullable=False), sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False), sa.Column("checksum_sha256", sa.String(64), nullable=False), sa.Column("uploaded_by_id", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["entry_id"], ["maintenance_log_entries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="RESTRICT"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("storage_key"),
    )
    for c in ("empresa_id","entry_id","checksum_sha256"): op.create_index(f"ix_maintenance_log_attachments_{c}", "maintenance_log_attachments", [c])
    op.create_table(
        "maintenance_log_events",
        sa.Column("id", sa.Integer(), nullable=False), sa.Column("empresa_id", sa.Integer(), nullable=False), sa.Column("entry_id", sa.Integer(), nullable=False),
        sa.Column("event", sa.String(48), nullable=False), sa.Column("actor_id", sa.Integer(), nullable=False), sa.Column("detail", sa.String(500), nullable=False, server_default=""), sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT"), sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entry_id"], ["maintenance_log_entries.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"),
    )
    for c in ("empresa_id","entry_id","event","created_at"): op.create_index(f"ix_maintenance_log_events_{c}", "maintenance_log_events", [c])


def downgrade():
    op.drop_table("maintenance_log_events"); op.drop_table("maintenance_log_attachments"); op.drop_table("maintenance_log_entries")
