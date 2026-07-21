"""Evidencias, conformidad, firma y revisión de checklist.

Revision ID: ip7f3h59m82x
Revises: hn6e2g48l71w
"""

from alembic import op
import sqlalchemy as sa

revision = "ip7f3h59m82x"
down_revision = "hn6e2g48l71w"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("work_order_checklists") as batch:
        batch.add_column(sa.Column("reviewed_by_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("reviewed_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("review_notes", sa.String(500), nullable=False, server_default=""))
        batch.create_foreign_key("fk_checklist_reviewed_by", "users", ["reviewed_by_id"], ["id"], ondelete="RESTRICT")
    with op.batch_alter_table("work_order_checklist_responses") as batch:
        batch.add_column(sa.Column("conformity", sa.String(24), nullable=False, server_default="pending_review"))
        batch.add_column(sa.Column("justification", sa.String(500), nullable=False, server_default=""))
        batch.add_column(sa.Column("resolution_note", sa.String(500), nullable=False, server_default=""))
        batch.add_column(sa.Column("resolved_by_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("resolved_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("signed_at", sa.DateTime(), nullable=True))
        batch.add_column(sa.Column("signature_name_snapshot", sa.String(160), nullable=False, server_default=""))
        batch.add_column(sa.Column("signature_purpose", sa.String(255), nullable=False, server_default=""))
        batch.create_foreign_key("fk_checklist_response_resolved_by", "users", ["resolved_by_id"], ["id"], ondelete="RESTRICT")
        batch.create_check_constraint("ck_checklist_response_conformity", "conformity in ('conforming','nonconforming','not_applicable','pending_review')")
    op.create_table(
        "work_order_checklist_evidences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa_id", sa.Integer(), nullable=False),
        sa.Column("checklist_id", sa.Integer(), nullable=False),
        sa.Column("response_id", sa.Integer(), nullable=False),
        sa.Column("step_id", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("original_name", sa.String(255), nullable=False),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("uploaded_by_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["checklist_id"], ["work_order_checklists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["empresa_id"], ["empresas.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["response_id"], ["work_order_checklist_responses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["step_id"], ["maintenance_procedure_steps.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    for column in ("empresa_id", "checklist_id", "response_id", "step_id", "checksum_sha256"):
        op.create_index(f"ix_work_order_checklist_evidences_{column}", "work_order_checklist_evidences", [column])


def downgrade():
    op.drop_table("work_order_checklist_evidences")
    with op.batch_alter_table("work_order_checklist_responses") as batch:
        batch.drop_constraint("ck_checklist_response_conformity", type_="check")
        batch.drop_constraint("fk_checklist_response_resolved_by", type_="foreignkey")
        for column in ("signature_purpose", "signature_name_snapshot", "signed_at", "resolved_at", "resolved_by_id", "resolution_note", "justification", "conformity"):
            batch.drop_column(column)
    with op.batch_alter_table("work_order_checklists") as batch:
        batch.drop_constraint("fk_checklist_reviewed_by", type_="foreignkey")
        for column in ("review_notes", "reviewed_at", "reviewed_by_id"):
            batch.drop_column(column)
