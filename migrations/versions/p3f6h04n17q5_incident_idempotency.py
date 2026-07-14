"""incident idempotency

Revision ID: p3f6h04n17q5
Revises: o2e5g93m06n4
"""
from alembic import op
import sqlalchemy as sa


revision = "p3f6h04n17q5"
down_revision = "o2e5g93m06n4"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("incidents") as batch_op:
        batch_op.add_column(sa.Column("idempotency_key", sa.String(length=36), nullable=True))
        batch_op.create_index("ix_incidents_idempotency_key", ["idempotency_key"], unique=True)


def downgrade():
    with op.batch_alter_table("incidents") as batch_op:
        batch_op.drop_index("ix_incidents_idempotency_key")
        batch_op.drop_column("idempotency_key")
